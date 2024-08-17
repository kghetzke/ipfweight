import pandas as pd
import numpy as np
import logging


class WeightingSchema():
    def __init__(self, data: pd.DataFrame, **targets):
        self.data = data.copy()
        self.targets = targets
        self.weights = None

        #Confirm each target column exists in the data,
        for target, vals in self.targets.items():
            if target not in self.data.columns:
                raise ValueError(f"Target column '{target}' not found in data.")
            # Confirm that values specified in each target is a dictionary,
            if not isinstance(vals, dict):
                raise ValueError(f"Values for '{target}' must be specified as a dictionary.")
            # Confirm that values specified in the targets exist in the target column,
            val_total = 0
            for val in vals.keys():
                if val not in self.data[target].unique():
                    raise ValueError(f"Value '{val}' not found in column '{target}'.")
                val_total += vals[val]
            if val_total != 100:
                raise ValueError(f"Values for '{target}' do not sum to 100.")
            # Confirm if there are values present in target column not specified in the targets schema,
            if len(self.data[target].unique()) > len(vals.keys()):
                value_list = [val for val in self.data[target].unique() if val not in vals.keys()]
                raise ValueError(f"The following values exist in data for '{target}' that are not specified in the target schema: {value_list}")
            
        self.targets_na = self.check_na()
        return
    
    def check_na(self):
        missing_counts = pd.DataFrame(self.data[[target for target in self.targets.keys()]].isna().sum(), columns=['NA_Count']).reset_index().rename(columns={'index':'Target'})
        if missing_counts['NA_Count'].sum() > 0:
            logging.warning(f"Missing values found in in the following target columns: {missing_counts.query('NA_Count > 0')['Target'].tolist()}")
            return True
        else:
            return False
        

    def fit(self, max_iter=500, tol=0.1, max=None, min=None, allow_missings=False):

        # Don't proceed if we don't want to allow missing values in target columns
        if allow_missings==False and self.targets_na==True:
            raise ValueError("Missing values found in target columns. Please specify 'allow_missings=True' to allow missing values in target columns.")

        # Initialize weights as 1 for all observations, and begin iterative proportional fitting loop
        weights = np.ones(self.data.shape[0])

        for iteration in range(max_iter):
            for target, vals in self.targets.items():

                # We're going to temporarily copy "weights" as "new_weights", to perform adjustments based on current target variable
                new_weights = weights * 1
                weighted_sum_total = (new_weights * np.where(self.data[target].isna(),0,1)).sum()
                
                # For each value in the target variable, calculate the sample margin based on current weights and then adjust weights accordingly 
                for level in vals.keys():
                    weighted_sum_level = (new_weights * np.where(self.data[target]==level,1,0)).sum()
                    sample_margin = weighted_sum_level / weighted_sum_total
                    new_weights = np.where(self.data[target] == level, (vals[level] / sample_margin)*0.01, new_weights)
                
                # Adjust for missing values in target variable if we want to allow them
                if allow_missings==True and self.targets_na==True:
                    new_weights = np.where(self.data[target].isna(), 1, new_weights)
                
                # Adjust the previously calculated weights with the newly calculated weights based on current target variable
                weights = weights * new_weights

                # If max/min thresholds are specified, trim weights after applying mean-correction
                if max is not None:
                    weights = weights / weights.mean()
                    weights = np.where(weights > max, max, weights)
                if min is not None:
                    weights = weights / weights.mean()
                    weights = np.where(weights < min, min, weights)

                # Perform final mean-correction on weights
                weights = weights / weights.mean()

            # Check to see if tolerance criteria has been reached
            all_differences = []
            for target, vals in self.targets.items():
                for level in vals.keys():
                    achieved_proportion = (weights * np.where(self.data[target] == level, 1, 0)).mean() * 100
                    desired_proportion = vals[level]
                    all_differences.append(np.abs(achieved_proportion - desired_proportion))
            all_differences.sort()
            largest_difference = all_differences[-1]
            if largest_difference < tol:
                logging.info(f'Tolerance criteria reached after {iteration+1} iterations.')
                self.weights = weights
                return weights
        # If we make it through all iterations without achieving tolerance criteria, then 
        logging.warning(f'Tolerance criteria not reached after {max_iter} iterations.')
        self.weights = weights
        return weights
    
    # Function to apply weights to the data and return unweighted-counts/percentages vs weighted-counts/percentages
    def summary(self):
        if self.weights is None:
            raise ValueError("No weights have been calculated yet.")
        targets_df = pd.DataFrame(self.targets).stack().reset_index()[['level_1','level_0',0]].rename(columns={'level_1':'Variable','level_0':'Var-Level',0:'Target-Percentage'})
        summary_dfs = []
        for var in self.targets.keys():
            temp_df = self.data.copy()
            temp_df['Unweighted-Percentage'] = 1
            temp_df['Weighted-Percentage'] = self.weights
            temp_df = ((temp_df.groupby(var).agg({'Unweighted-Percentage':'sum','Weighted-Percentage':'sum'}) / temp_df.agg({'Unweighted-Percentage':'sum','Weighted-Percentage':'sum'}))*100).reset_index().rename(columns={var:'Var-Level'})
            temp_df['Variable'] = var
            summary_dfs.append(temp_df)
        return targets_df.merge(pd.concat(summary_dfs), on=['Variable','Var-Level'], how='left')[['Variable','Var-Level','Unweighted-Percentage','Target-Percentage','Weighted-Percentage']]
