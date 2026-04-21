import matplotlib.pyplot as plt

def visualize_full_float_range(M, E):
    """
    M: Number of mantissa (fractional) bits
    E: Number of exponent bits
    """
    # 1. Calculate Constants
    bias = 2**(E - 1) - 1
    e_min = 1 - bias
    e_max = (2**E - 2) - bias
    
    # 2. Subnormal Region
    # Smallest non-zero value (Smallest Subnormal)
    smallest_subnormal = 2**(e_min - M)
    # The step size is constant for all subnormals
    step_subnormal = 2**(e_min - M)
    
    # 3. Build the data points
    # We start from the smallest subnormal because 0 cannot be plotted on log scale
    x = [smallest_subnormal, 2**e_min]
    y = [step_subnormal, step_subnormal]
    
    # 4. Normalized Region
    # For every exponent from e_min to e_max
    for e in range(e_min, e_max + 1):
        val_start = 2**e
        val_end = 2**(e + 1)
        step = 2**(e - M)
        
        # Add the points to create the "staircase"
        x.extend([val_start, val_end])
        y.extend([step, step])
    
    # 5. Plotting
    plt.figure(figsize=(12, 6))
    
    # We use plot with 'x' and 'y' data; because we duplicated points, 
    # it naturally looks like a step function.
    plt.plot(x, y, label=f"Step Size (Gap)", color='#1f77b4', linewidth=2)
    
    # Formatting
    # plt.xscale('log', base=2)
    # plt.yscale('log', base=2)
    
    plt.title(f"Float Precision Map (M={M}, E={E})", fontsize=14)
    plt.xlabel("Decimal Value (Magnitude)", fontsize=12)
    plt.ylabel("Smallest Possible Step (ULP)", fontsize=12)
    
    plt.grid(True, which="both", ls="-", alpha=0.3)
    
    # Calculate and mark the Max Value
    max_val = (2 - 2**(-M)) * 2**e_max
    plt.axvline(x=max_val, color='r', linestyle='--', alpha=0.5, label=f"Max Value (~{max_val:.1e})")
    plt.ylim(bottom=0)
    
    plt.ticklabel_format(style="plain", axis="x")
    plt.ticklabel_format(style="plain", axis="y")
    maxX = 1000
    plt.xlim(0, maxX)
    max_step_in_range = max([step for step, val in zip(y, x) if val <= maxX])
    plt.ylim(bottom=0, top=max_step_in_range * 1.1)

    plt.legend()
    plt.tight_layout()
    plt.show()

visualize_full_float_range(M=13, E=6)