import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import platform
import webbrowser

def is_display_available():
    if platform.system() == 'Linux':
        return "DISPLAY" in os.environ
    return True

# Constants
epsilon_0 = 8.854e-12  # Permittivity of free space (F/m)
q = 1.602e-19          # Electron charge (C)


# Process .txt files and convert to .xlsx
def process_txt_file(file_path):
    filename = os.path.basename(file_path)
    frequency = filename.split('kHz')[0] + 'kHz' if 'kHz' in filename else "Unknown"

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = file.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='ISO-8859-1') as file:
            data = file.read()
        print(f"File '{filename}' decoded using ISO-8859-1 encoding.")
    
    data = data.replace(',', '.')

    lines = data.split('\n')
    filtered_lines = [line for line in lines if len(line.split()) >= 3]

    if not filtered_lines:
        print(f"Warning: File {filename} is empty after filtering. Skipping...")
        return None, None, None

    df = pd.read_csv(io.StringIO("\n".join(filtered_lines)), sep=r'\s+', header=None)
    
    if df.shape[1] < 3:
        print(f"Error: File {filename} does not have enough valid columns.")
        return None, None, None
    
    df = df.iloc[:, :3]  
    df.columns = ['Voltage(V)', 'C_Forward(F)', 'C_Backward(F)']
    
    df = df.dropna()
    
    return df, frequency, filename


def calculate_ncv_zcv(df, A, epsilon_r):
    voltage = df['Voltage(V)']
    capacitance_forward = df['C_Forward(F)']
    capacitance_backward = df['C_Backward(F)']

    dV_dC_forward = np.gradient(voltage) / np.gradient(capacitance_forward)
    dV_dC_backward = np.gradient(voltage) / np.gradient(capacitance_backward)

    dV_dC_forward = np.nan_to_num(dV_dC_forward, nan=0.0, posinf=1e10, neginf=-1e10)
    dV_dC_backward = np.nan_to_num(dV_dC_backward, nan=0.0, posinf=1e10, neginf=-1e10)

    Ncv_forward = (capacitance_forward**3 / (epsilon_0 * epsilon_r * A**2 * q)) * dV_dC_forward
    Ncv_backward = (capacitance_backward**3 / (epsilon_0 * epsilon_r * A**2 * q)) * dV_dC_backward

    Zcv_forward = (epsilon_0 * epsilon_r * A) / capacitance_forward
    Zcv_backward = (epsilon_0 * epsilon_r * A) / capacitance_backward

    Ncv_forward_cm3 = np.abs(Ncv_forward * 1e-6)
    Ncv_backward_cm3 = np.abs(Ncv_backward * 1e-6)
    integrated_Ncv_forward = np.trapezoid(Ncv_forward_cm3, Zcv_forward * 1e9)
    integrated_Ncv_backward = np.trapezoid(Ncv_backward_cm3, Zcv_backward * 1e9)

    result_df = pd.DataFrame({
        'Voltage(V)': voltage,
        'Zcv_Forward (nm)': Zcv_forward * 1e9,
        'Zcv_Backward (nm)': Zcv_backward * 1e9,
        'Ncv_Forward (cm^-3)': Ncv_forward_cm3,
        'Ncv_Backward (cm^-3)': Ncv_backward_cm3
    })
    
    return result_df, integrated_Ncv_forward, integrated_Ncv_backward


def extract_sample_name(filename):
    import re
    match = re.search(r'C\(V\)_0_([A-Za-z0-9]+)_', filename)
    if match:
        return match.group(1)
    return "Unknown"

def run_cli_mode():
    import argparse
    print("Running in CLI mode. No GUI available.")
    parser = argparse.ArgumentParser(description="CLI Mode for Ncv and Zcv Calculation")
    parser.add_argument("--files", nargs='+', required=True, help="List of .txt files to process")
    parser.add_argument("--diameter", type=float, required=True, help="Capacitor diameter in µm")
    parser.add_argument("--epsilon", type=float, required=True, help="Relative permittivity (εr)")
    parser.add_argument("--interface", type=float, required=True, help="Expected interface depth (nm)")

    args = parser.parse_args()

    radius_m = (args.diameter * 1e-6) / 2
    A = np.pi * radius_m**2

    print(f"Capacitor Area: {A:.4e} m²")
    print(f"Relative Permittivity: {args.epsilon}")

    results = {}
    sample_names = set()

    for file_path in args.files:
        df, frequency, filename = process_txt_file(file_path)
        if df is not None:
            sample_name = extract_sample_name(filename)
            sample_names.add(sample_name)
            results_df, Ncv_f, Ncv_b = calculate_ncv_zcv(df, A, args.epsilon)
            results[frequency] = (results_df, Ncv_f, Ncv_b)
            print(f"{frequency}: Forward Sheet Carrier Density: {Ncv_f:.2e} cm^-2")
            print(f"{frequency}: Backward Sheet Carrier Density: {Ncv_b:.2e} cm^-2")

    if len(sample_names) > 1:
        print(f"Error: Multiple sample names detected: {sample_names}. Please ensure all files belong to the same sample.")
        return

    sample_name = sample_names.pop() if sample_names else "Unknown"
    output_folder = os.path.join(os.getcwd(), f"Results_{sample_name}")
    os.makedirs(output_folder, exist_ok=True)

    # Save results to Excel
    output_file = os.path.join(output_folder, f'Ncv_Zcv_Results_{sample_name}.xlsx')
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        for frequency, (data, _, _) in results.items():
            data.to_excel(writer, sheet_name=frequency, index=False)
    print(f"Results saved to {output_file}")

    # Plotting
    fig, axes = plt.subplots(len(results), 2, figsize=(14, 12))

    for i, (frequency, (data, Ncv_f, Ncv_b)) in enumerate(results.items()):
        ax_forward = axes[i, 0]
        ax_forward.plot(data['Zcv_Forward (nm)'], data['Ncv_Forward (cm^-3)'], marker='o', color='red')
        ax_forward.axvline(args.interface, color='orange', linestyle='--', label='Interface Depth')
        ax_forward.set_title(f'{frequency} - Forward')
        ax_forward.set_yscale('log')
        ax_forward.grid(True)

        ax_backward = axes[i, 1]
        ax_backward.plot(data['Zcv_Backward (nm)'], data['Ncv_Backward (cm^-3)'], marker='x', color='black')
        ax_backward.axvline(args.interface, color='orange', linestyle='--', label='Interface Depth')
        ax_backward.set_title(f'{frequency} - Backward')
        ax_backward.set_yscale('log')
        ax_backward.grid(True)

    plot_file = os.path.join(output_folder, f'Ncv_vs_Zcv_Plots_{sample_name}.png')
    fig.savefig(plot_file)
    print(f"Plots saved to {plot_file}")

    plt.close(fig)

class NcvZcvApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ncv and Zcv Calculator")
        self.root.geometry("700x500")
        self.file_paths = []
        self.results = {}

        self.create_widgets()

    def create_widgets(self):
        Label(self.root, text="Ncv and Zcv Calculator", font=("Helvetica", 18)).pack(pady=10)

        formula_frame = Frame(self.root)
        formula_frame.pack(pady=15)
        Label(formula_frame, text="Formulae:").pack()
        Label(formula_frame, text="Ncv = (C^3 / (ε₀ * εr * A² * q)) * (dV/dC)", font=("Helvetica", 12)).pack()
        Label(formula_frame, text="Zcv = (ε₀ * εr * A) / C", font=("Helvetica", 12)).pack()
        Label(formula_frame, text="Sheet Carrier Density (σ) = ∫ Ncv dZcv", font=("Helvetica", 12)).pack()
        link = Label(formula_frame, text="DOI: 10.1063/1.371866", font=('Helvetica', 10, 'underline'), fg="blue", cursor="hand2")
        link.pack()
        link.bind("<Button-1>", lambda e: webbrowser.open_new("https://doi.org/10.1063/1.371866"))

        self.select_button = Button(self.root, text="Select C(V) Files", command=self.select_files)
        self.select_button.pack(pady=20)

        self.diameter_var = StringVar()
        self.epsilon_var = StringVar()
        self.interface_var = StringVar()

        self.create_input_fields()
        self.process_button = Button(self.root, text="Process and Plot", command=self.process_data)
        self.process_button.pack(pady=30)

    def create_input_fields(self):
        Label(self.root, text="Capacitor Diameter (µm):").pack()
        Entry(self.root, textvariable=self.diameter_var).pack()

        Label(self.root, text="Relative Permittivity (εr):").pack()
        Entry(self.root, textvariable=self.epsilon_var).pack()

        Label(self.root, text="Expected Interface Depth (nm):").pack()
        Entry(self.root, textvariable=self.interface_var).pack()

    def select_files(self):
        self.file_paths = filedialog.askopenfilenames(
            title="Select C(V) .txt Files",
            filetypes=[("Text Files", "*.txt")]
        )
        sample_names = [extract_sample_name(os.path.basename(file)) for file in self.file_paths]
        if len(set(sample_names)) != 1:
            messagebox.showerror("Error", f"Files belong to different samples: {set(sample_names)}")
            self.file_paths = []
        else:
            messagebox.showinfo("Success", f"{len(self.file_paths)} files selected from sample: {sample_names[0]}")

    def process_data(self):
        if not self.file_paths:
            messagebox.showerror("Error", "No files selected.")
            return

        try:
            diameter_um = float(self.diameter_var.get())
            epsilon_r = float(self.epsilon_var.get())
            interface_z = float(self.interface_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for diameter, εr, and interface depth.")
            return

        radius_m = (diameter_um * 1e-6) / 2
        A = np.pi * radius_m**2

        self.results = {}
        sample_names = set()
        for file_path in self.file_paths:
            df, frequency, filename = process_txt_file(file_path)
            if df is not None:
                sample_name = extract_sample_name(filename)
                sample_names.add(sample_name)
                results_df, Ncv_f, Ncv_b = calculate_ncv_zcv(df, A, epsilon_r)
                self.results[frequency] = (results_df, Ncv_f, Ncv_b)

        if len(sample_names) > 1:
            messagebox.showerror("Error", f"Files belong to different samples: {sample_names}")
            return

        sample_name = sample_names.pop() if sample_names else "Unknown"
        self.plot_results(interface_z, sample_name)

    def plot_results(self, interface_z, sample_name):
        fig, axes = plt.subplots(len(self.results), 2, figsize=(14, 12))

        if len(self.results) == 1:
            axes = np.array([axes])

        for i, (frequency, (data, Ncv_f, Ncv_b)) in enumerate(self.results.items()):
            # Forward Plot (Left Column)
            ax_forward = axes[i, 0]
            ax_forward.plot(
                data['Zcv_Forward (nm)'],
                data['Ncv_Forward (cm^-3)'],
                marker='o',
                color='red',
                label=f'{frequency} Forward\nSheet Carrier Density = {Ncv_f:.2e} cm^-2'
            )
            ax_forward.set_title(f'Forward - {frequency}', fontsize=10, loc='left')
            ax_forward.axvline(interface_z, color='orange', linestyle='--', label='Interface Depth (Z)')
            ax_forward.set_xlabel('Zcv (nm)')
            ax_forward.set_ylabel('Ncv (cm^-3)')
            ax_forward.set_yscale('log')
            ax_forward.grid(True)
            ax_forward.legend(loc='upper right')

            # Backward Plot (Right Column)
            ax_backward = axes[i, 1]
            ax_backward.plot(
                data['Zcv_Backward (nm)'],
                data['Ncv_Backward (cm^-3)'],
                marker='o',
                color='black',
                label=f'{frequency} Backward\nSheet Carrier Density = {Ncv_b:.2e} cm^-2'
            )
            ax_backward.set_title(f'Backward - {frequency}', fontsize=10, loc='left')
            ax_backward.axvline(interface_z, color='orange', linestyle='--', label='Interface Depth (Z)')
            ax_backward.set_xlabel('Zcv (nm)')
            ax_backward.set_ylabel('Ncv (cm^-3)')
            ax_backward.set_yscale('log')
            ax_backward.grid(True)
            ax_backward.legend(loc='upper right')

        plt.tight_layout()
        plt.show()

        # Save plots and data
        output_folder = os.path.join(os.getcwd(), f"Results_{sample_name}")
        os.makedirs(output_folder, exist_ok=True)

        plot_file = os.path.join(output_folder, f'Ncv_vs_Zcv_Plots_{sample_name}.png')
        fig.savefig(plot_file)
        messagebox.showinfo("Success", f"Plots saved to {plot_file}")

        self.save_to_excel(output_folder, sample_name)

    def save_to_excel(self, output_folder, sample_name):
        output_file = os.path.join(output_folder, f'Ncv_Zcv_Results_{sample_name}.xlsx')
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            for frequency, (data, _, _) in self.results.items():
                data.to_excel(writer, sheet_name=frequency, index=False)

        messagebox.showinfo("Success", f"Results saved to {output_file}")


if __name__ == "__main__":
    if is_display_available():
        from tkinter import Tk, filedialog, Label, Button, Entry, StringVar, messagebox, Frame
        root = Tk()
        app = NcvZcvApp(root)
        root.mainloop()
    else:
        run_cli_mode()
