import general_maths_formulas as formulas

def capm_beta(rp, rm):
    return formulas.covariance(rp, rm)/formulas.variance(rm)
