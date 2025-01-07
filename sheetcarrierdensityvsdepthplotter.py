import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from tkinter import Tk, filedialog, simpledialog, Label, Button, Entry, StringVar, messagebox, Frame
from datetime import datetime

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
    
    # Replace commas in numerical values only
    data = data.replace(',', '.')

    # Keep lines with at least 3 columns
    lines = data.split('\n')
    filtered_lines = [line for line in lines if len(line.split()) >= 3]

    if not filtered_lines:
        print(f"Warning: File {filename} is empty after filtering. Skipping...")
        return None, None, None

    # Parse the filtered data into a DataFrame
    df = pd.read_csv(io.StringIO("\n".join(filtered_lines)), sep=r'\s+', header=None)
    
    if df.shape[1] < 3:
        print(f"Error: File {filename} does not have enough valid columns.")
        return None, None, None
    
    # Keep the first 3 columns and rename them
    df = df.iloc[:, :3]  
    df.columns = ['Voltage(V)', 'C_Forward(F)', 'C_Backward(F)']
    
    # Handle NaN values
    df = df.dropna()
    
    return df, frequency, filename


def calculate_ncv_zcv(df, A, epsilon_r):
    voltage = df['Voltage(V)']
    capacitance_forward = df['C_Forward(F)']
    capacitance_backward = df['C_Backward(F)']

    dV_dC_forward = np.gradient(voltage) / np.gradient(capacitance_forward)
    dV_dC_backward = np.gradient(voltage) / np.gradient(capacitance_backward)

    # Handle large gradients by replacing NaN and inf values
    dV_dC_forward = np.nan_to_num(dV_dC_forward, nan=0.0, posinf=1e20, neginf=-1e20)
    dV_dC_backward = np.nan_to_num(dV_dC_backward, nan=0.0, posinf=1e20, neginf=-1e20)

    Ncv_forward = (capacitance_forward**3 / (epsilon_0 * epsilon_r * A**2 * q)) * dV_dC_forward
    Ncv_backward = (capacitance_backward**3 / (epsilon_0 * epsilon_r * A**2 * q)) * dV_dC_backward

    Zcv_forward = (epsilon_0 * epsilon_r * A) / capacitance_forward
    Zcv_backward = (epsilon_0 * epsilon_r * A) / capacitance_backward

    # Integrate Ncv over Zcv to get sheet carrier density
    Ncv_forward_cm3 = np.abs(Ncv_forward * 1e-6)
    Ncv_backward_cm3 = np.abs(Ncv_backward * 1e-6)
    integrated_Ncv_forward = np.trapz(Ncv_forward_cm3, Zcv_forward * 1e9)
    integrated_Ncv_backward = np.trapz(Ncv_backward_cm3, Zcv_backward * 1e9)

    result_df = pd.DataFrame({
        'Voltage(V)': voltage,
        'Zcv_Forward (nm)': Zcv_forward * 1e9,
        'Zcv_Backward (nm)': Zcv_backward * 1e9,
        'Ncv_Forward (cm^-3)': Ncv_forward_cm3,
        'Ncv_Backward (cm^-3)': Ncv_backward_cm3
    })
    
    return result_df, integrated_Ncv_forward, integrated_Ncv_backward


# GUI Application
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

        # Formula Section
        formula_frame = Frame(self.root)
        formula_frame.pack(pady=15)
        Label(formula_frame, text="Formulas:").pack()
        Label(formula_frame, text="Ncv = (C^3 / (ε₀ * εr * A² * q)) * (dV/dC)", font=("Helvetica", 12)).pack()
        Label(formula_frame, text="Zcv = (ε₀ * εr * A) / C", font=("Helvetica", 12)).pack()
        Label(formula_frame, text="Sheet Carrier Density (σ) = ∫ Ncv dZcv", font=("Helvetica", 12)).pack()

        # File Selection Button
        self.select_button = Button(self.root, text="Select C(V) Files", command=self.select_files)
        self.select_button.pack(pady=20)

        # Input Fields
        self.diameter_var = StringVar()
        self.epsilon_var = StringVar()
        self.interface_var = StringVar()

        self.create_input_fields()

        # Process Button
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
        if not self.file_paths:
            messagebox.showwarning("Warning", "No files selected.")
        else:
            messagebox.showinfo("Success", f"{len(self.file_paths)} files selected.")

    def process_data(self):
        if not self.file_paths:
            messagebox.showerror("Error", "No files selected.")
            return
        
        diameter_um = float(self.diameter_var.get())
        epsilon_r = float(self.epsilon_var.get())
        interface_z = float(self.interface_var.get())

        radius_m = (diameter_um * 1e-6) / 2
        A = np.pi * radius_m**2

        for file_path in self.file_paths:
            df, frequency, _ = process_txt_file(file_path)
            if df is not None:
                results_df, Ncv_f, Ncv_b = calculate_ncv_zcv(df, A, epsilon_r)
                self.results[frequency] = (results_df, Ncv_f, Ncv_b)

        self.plot_results(interface_z)

    def plot_results(self, interface_z):
        fig, axes = plt.subplots(len(self.results), 2, figsize=(14, 12))
        
        # Check if axes is not multi-dimensional (for a single frequency case)
        if len(self.results) == 1:
            axes = np.array([axes])

        # Iterate through results to plot Ncv vs Zcv
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
            ax_forward.set_title(f'Forward - {frequency}', fontsize=10, loc = 'left')  # Smaller title
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
            ax_backward.set_title(f'Backward - {frequency}', fontsize=10, loc = 'left')  # Smaller title
            ax_backward.axvline(interface_z, color='orange', linestyle='--', label='Interface Depth (Z)')
            ax_backward.set_xlabel('Zcv (nm)')
            ax_backward.set_ylabel('Ncv (cm^-3)')
            ax_backward.set_yscale('log')
            ax_backward.grid(True)
            ax_backward.legend(loc='upper right', fontsize='small')

        plt.tight_layout()
        plt.show()


        
if __name__ == "__main__":
    root = Tk()
    app = NcvZcvApp(root)
    root.mainloop()
