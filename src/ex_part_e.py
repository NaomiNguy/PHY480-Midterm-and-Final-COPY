print("Best-fit parameters:")
print(f"P     = {best_params['period']:.6f} ± {uncertainties['period_std']:.6f} days")
print(f"delta = {best_params['depth']:.6f} ± {uncertainties['depth_std']:.6f}")
print(f"tau   = {best_params['duration']:.6f} ± {uncertainties['duration_std']:.6f} days")
print(f"t0    = {best_params['epoch']:.6f} ± {uncertainties['epoch_std']:.6f} days")

phase = (((t - best_params["epoch"]) / best_params["period"] + 0.5) % 1.0) - 0.5
order = np.argsort(phase)

phase_sorted = phase[order]
flux_sorted = flux[order]

model_sorted = box_transit_model(
    t,
    best_params["period"],
    best_params["depth"],
    best_params["duration"],
    best_params["epoch"],
)[order]

plt.figure(figsize=(8, 4))
plt.scatter(phase_sorted, flux_sorted, s=6, label="Data")
plt.plot(phase_sorted, model_sorted, linewidth=2, label="Best-fit model")
plt.xlabel("Phase")
plt.ylabel("Flux")
plt.title("Folded Light Curve with Transit Model")
plt.legend()
plt.tight_layout()
plt.show()