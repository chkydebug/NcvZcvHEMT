# Ncv and Zcv Calculator (Tkinter GUI)

This application calculates **Carrier Density** $N_{cv}$($cm^{-3}$) and **Depth** $Z_{cv}$ $(nm)$ from **$C(V)$** data files using a **Tkinter GUI** interface. It supports plotting and visualization of forward and backward capacitance sweeps to derive key parameters for High Electron Mobility Transistors (HEMTs) and similar semiconductor structures.

---

### **Features**  
- **Graphical User Interface (GUI):** Simple Tkinter-based interface for file selection and input.  
- **Multiple File Support:** Process multiple C(V) text files at different frequencies.  
- **Plotting:** Generates $N_{cv}$ vs $Z_{cv}$ plots with forward and backward sweeps on a log scale.  
- **Sheet Carrier Density Integration:** Automatically calculates sheet carrier density using:  
 $$\sigma_{cv} = \int N_{cv} \, dZ_{cv}$$ 

- **User Inputs:**  
   - Capacitor diameter (in µm).  
   - Relative permittivity $\varepsilon_r$.  
   - Expected interface depth (in nm) for visualization.  

---

### **Formulas Used**  
- **Carrier Density** $N_{cv}$:  
  $$N_{cv} = \frac{C^3}{\varepsilon_0 \varepsilon_r A^2 q} \cdot \frac{dV}{dC}$$ 

- **Depth** $Z_{cv}$:  
  $$Z_{cv} = \frac{\varepsilon_0 \varepsilon_r A}{C}$$ 

- **Sheet Carrier Density** $\sigma_{cv}$:  
  $$\sigma_{cv} = \int N_{cv} dZ_{cv}$$ 

Where:  
- $$\varepsilon_0 = 8.854 \times 10^{-12} \, F/m$$ (Permittivity of free space)  
- $$q = 1.602 \times 10^{-19} \, C$$ (Electron charge)  
- $A$ is the area of the capacitor  
  $$A =\pi\left(\frac{d}{2}\right)^2$$  
- $C$ is capacitance, and $\frac{dV}{dC}$ is the voltage derivative.  

---

### **Installation**  
1. **Clone the Repository**  
   ```bash
   git clone https://github.com/chkydebug/NcvZcvHEMT.git
   cd NcvZcvHEMT
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

---

### **Running the Application**
```bash
python sheetcarrierdensityvsdepthplotter.py
```

- The GUI will open and prompt for file selection and necessary input parameters.

---

### **Usage**
1. **Select C(V) Data Files**
   Click "Select C(V) Files" and choose the `.txt` files containing capacitance-voltage data.

2. **Input Parameters**
   - Enter **capacitor diameter** in µm.
   - Specify $\varepsilon_r$ (relative permittivity).
   - Provide the **expected interface depth** for visualization.

3. **Process and Plot**
   Click "Process and Plot" to generate $N_{cv}$ vs $Z_{cv}$ plots. The sheet carrier density will be displayed in the legend.

---

### **Output**
- Plots showing $N_{cv}$ vs $Z_{cv}$ for forward and backward sweeps.
- Visualization of the interface depth marked by an orange vertical line.
- Calculated sheet carrier densities will appear in the legend of each plot.

---

### **Building an Executable (.exe)**
To build an executable using **PyInstaller**:
```bash
pyinstaller --onefile --windowed sheetcarrierdensityvsdepthplotter.py
```

The executable will be created in the `dist` directory.

---

### **License**
This project is licensed under the MIT License.

---
```
