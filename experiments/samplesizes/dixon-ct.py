from statsmodels.stats.power import NormalIndPower

effect_size = 0.7
alpha = 0.05
power = 0.8

power_analysis = NormalIndPower()
sample_size = power_analysis.solve_power(effect_size=effect_size, alpha=alpha, power=power, alternative='two-sided')

print(f'Required sample size: {sample_size}')