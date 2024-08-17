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
Running the code above would return the following table:

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Variable</th>
      <th>Var-Level</th>
      <th>Unweighted-Percentage</th>
      <th>Target-Percentage</th>
      <th>Weighted-Percentage</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Gender</td>
      <td>Male</td>
      <td>43.2</td>
      <td>48.5</td>
      <td>48.463307</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Gender</td>
      <td>Female</td>
      <td>56.8</td>
      <td>51.5</td>
      <td>51.536693</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Age</td>
      <td>18 to 24</td>
      <td>16.6</td>
      <td>12.0</td>
      <td>12.001133</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Age</td>
      <td>25 to 34</td>
      <td>15.3</td>
      <td>17.0</td>
      <td>17.001742</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Age</td>
      <td>35 to 44</td>
      <td>14.2</td>
      <td>16.0</td>
      <td>15.992999</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Age</td>
      <td>45 to 64</td>
      <td>29.6</td>
      <td>33.0</td>
      <td>33.005526</td>
    </tr>
    <tr>
      <th>6</th>
      <td>Age</td>
      <td>65 to 84</td>
      <td>19.7</td>
      <td>19.0</td>
      <td>18.998184</td>
    </tr>
    <tr>
      <th>7</th>
      <td>Age</td>
      <td>85 and older</td>
      <td>4.6</td>
      <td>3.0</td>
      <td>3.000417</td>
    </tr>
    <tr>
      <th>8</th>
      <td>Ethnicity</td>
      <td>White</td>
      <td>68.9</td>
      <td>57.8</td>
      <td>57.800277</td>
    </tr>
    <tr>
      <th>9</th>
      <td>Ethnicity</td>
      <td>Non-White</td>
      <td>31.1</td>
      <td>42.2</td>
      <td>42.199723</td>
    </tr>
  </tbody>
</table>



[^1]: Michael Bergmann, 2011. "IPFWEIGHT: Stata module to create adjustment weights for surveys," Statistical Software Components S457353, Boston College Department of Economics.
