# ipfweight

This package provides an implementation of an iterative proportional fitting algorithm for weighting survey samples to known population margins. The version of the algorithm in this package closely follows the version written for Stata users by Michael Bergmann, 2011[^1].

## Coming soon to PyPi

I am planning to publish this as my first public package available on PyPi. For now it can be installed directly through the github url, running the following command:

`python -m pip install ipfweight@git+https://github.com/kghetzke/ipfweight.git`

## Quick Start

The following code can be used as a quick-start tutorial for how to estimate weights using `ipfweight`.

Say we have 1,000 survey respondents from random sampling, and we want our survey-sample weighted to match the following population margins on age, gender, and ethnicity.
- 51.5% female, 48.5% Male
- 12% 18 to 24, 17% 25 to 34, 16% 35 to 44, 33% 45 to 64, 19% 65 to 84, and 3% 85+
- 57.8% White, 42.2% Non-White


```python
# Randomly generate dummy survey data, which does not match census margins
import pandas as pd
import numpy as np
n_obs = 1000
np.random.seed(42)
svy = pd.DataFrame({
    'Age': np.random.choice(['18 to 24','25 to 34','35 to 44','45 to 64','65 to 84','85 and older'], n_obs, p = [0.15,0.15,0.15,0.3,0.2,0.05]),
    'Gender': np.random.choice(['Male','Female'], n_obs, p=[0.45,0.55]),
    'Ethnicity': np.random.choice(['White','Non-White'], n_obs, p=[0.7,0.3])
})

# Import ipfweight, define the desired WeightingSchema, and estimate weights
from ipfweight import WeightingSchema
schema = WeightingSchema(
    svy, 
    Gender={'Male': 48.5,'Female': 51.5}, 
    Age={'18 to 24': 12,'25 to 34': 17,'35 to 44': 16,'45 to 64': 33,'65 to 84': 19, '85 and older': 3}, 
    Ethnicity={'White': 57.8, 'Non-White': 42.2}
)
weights = schema.fit(max_iter=500, tol=0.1, max=2, min=0.5)

# Call and print the summary() method to display weighted vs unweighted percentages
print(schema.summary())
```



[^1]: Michael Bergmann, 2011. "IPFWEIGHT: Stata module to create adjustment weights for surveys," Statistical Software Components S457353, Boston College Department of Economics.
