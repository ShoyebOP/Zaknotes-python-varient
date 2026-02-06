# **Grace Blackwell AI Workstations: Comparative Analysis**

**Overview**
This technical comparison examines various "desk-side" AI supercomputers utilizing the **NVIDIA Grace Blackwell (GB)** chip. While these machines share a common architecture, they differ in chassis design, thermal management, and storage configurations.

**Primary Hardware Specifications**
- **Compute Power:** $1$ Petaflop of AI performance.
- **Chipset:** Grace Blackwell (e.g., GB10).
- **CPU Cores:** $20$ Arm cores per unit (typically $10$ high-performance cores and $10$ energy-efficient cores).
- **Memory:** $128$ GB (Unified).
- **Applications:** Large Language Models (LLMs), vision models, AI agents, video generation, and training.
- **Operating System:** **DGXOS** (Ubuntu-based with pre-installed AI/ML toolkits).

---

### **Physical and Hardware Variations**

**Model Comparison**
1. **NVIDIA DGX Spark:** The reference design; features the cleanest aesthetic and best acoustic performance.
2. **ASUS Ascent GX10:** The heaviest model ($1474$ g); features a front-facing power button and a plastic top cover.
3. **Dell ProMax GB10:** Closest to the reference design; features a honeycomb grill and additional magnets for the rear panel.
4. **MSI Edge Expert:** Features the most detailed port labeling (e.g., PD out, DisplayPort, $20$ Gbps).

**Chassis & Portability**
- **Form Factor:** All units are too tall for a standard $1$U rack space.
- **Weight:** Most units hover around $1255$–$1257$ g, except for the ASUS GX10, which is significantly heavier (possibly due to enhanced copper cooling).
- **Connectivity:** Includes **ConnectX-7** ($200$G) or standard $10$G/QSFP ports, and HDMI $2.1$.

**Serviceability**
- **RAM:** Not user-swappable.
- **Storage:** The primary serviceable part is the **NVMe SSD** (size **$2242$**).
- **Access:** Spark and Dell use magnetic back panels to hide screws and legal text.

---

### **Thermal Performance and Power Management**

**Important Definitions**
- **Heat Soak:** The state reached (typically after $30$ minutes of operation) when the cooling system, heat sink, and internal air reach a steady temperature.
- **Thermal Throttling:** A hardware safety mechanism where CPU/GPU clock speeds are drastically reduced (e.g., $3$ GHz $\rightarrow$ $2$ GHz) because the system has exceeded critical temperature thresholds (e.g., $>100^\circ C$).
- **Software Power Capping:** An artificial limit set in software to prevent the system from drawing max power, regardless of temperature.

**Performance Data**
- **Acoustics:** Generally quiet. The **DGX Spark** is the quietest; the **MSI Edge Expert** is the loudest.
- **Temperatures:** Most units hover around $50^\circ C$ at steady-state, peaking near $80^\circ C$–$90^\circ C$ under extreme stress.
- **GPU Utilization:** High-performance inference (e.g., *Llama CPP*) utilizes $\approx 96\%$ of the GPU.

**The "John Carmack" Power Limit Observation**
*Context: Observation that the Spark maxes at $\approx 100$ W despite a $240$ W adapter.*
- The units are currently **Software Power Capped** at $\approx 100$ W for the GPU.
- This is **not** thermal throttling; clock speeds remain consistent even when the cap is hit.
- The **ASUS GX10** was the only unit to show a "Software Thermal Slowdown" event during extreme GPU burn tests, though the real-world performance impact remained negligible.

---

### **Storage and Data Transfer**

**NVMe Generations**
- **DGX Spark:** Utilizes **PCIe Gen 5** ($32$ GT/s).
- **ASUS/Dell/MSI:** Utilize **PCIe Gen 4** ($16$ GT/s).

**Performance Impact**
- **Sequential Transfers:** Gen $5$ reaches $\approx 13,000$ MB/s; Gen $4$ reaches $\approx 7,000$ MB/s.
- **Cold Starts:** *Gen 5* storage significantly reduces the time to load large models into memory.

---

### **Problem: Model Loading Efficiency**

**Question:**
Calculate the time difference in "Time to First Token" between a **PCIe Gen 5** system and a **PCIe Gen 4** system when loading a **Nemotron 30B** (unquantized) model.

**Solution:**
1. Identify the recorded loading times from the transcript.
2. Spark (Gen 5) loading time: $8.49$ seconds.
3. OEM units (Gen 4) loading time: $\approx 11.5$ seconds.
4. Calculate the delta: $11.5 - 8.49 = 3.01$ seconds.

**Explainer Notes:**
The primary advantage of **PCIe Gen 5** in AI workstations is not inference speed (which is compute-bound), but **Cold Start** efficiency. For agents frequently swapping between different large models, the $25\%$–$30\%$ faster load time is significant.

---

### **Summary of Results (Model Inference)**
*Model: Nemotron 30B (Unquantized)*

| Machine | Prompt Processing (TPS) | Token Generation (TPS) | Avg GPU Power Draw |
| :--- | :--- | :--- | :--- |
| **DGX Spark** | $1070$ | $61$ | $\approx 66$ W |
| **Dell GB10** | $1068$ | $61$ | $\approx 62.7$ W |
| **ASUS GX10** | $1068$ | $61$ | $\approx 60$ W |
| **MSI Edge** | $1068$ | $61$ | $\approx 60$ W |

**Important Note:** Despite physical and thermal differences, actual **Token Generation** performance is nearly identical across all Grace Blackwell desk-side models due to shared silicon and software limitations.