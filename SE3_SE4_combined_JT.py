"""
# Example: Sensor calibration and statistical methods 
 - Load data from example file and verify it is correct
     + Check that the Vaisala reference temperature column is present
     + Count the number of sensors in the data set
 - Ask user which sensor they wish to process (batch = False)
 - Process the specified sensors:
     + Split the data into training and testing sets 
     + Compute calibration curve using:
         - Naive regression using the entire training set without validation
         - Bootstrapping regression with validation metrics
     + Test naive and bootstrapping models against testing set
     + Append results into a CSV file
     + Display coefficients and fit, residual error plots (batch = False)

# Set batch = True to process all sensors present in example data
  - Note: code not threaded/MP, this may take hours.  

# Purpose of the script: 
   1) Compare individual sensor performance (batch = False)
   2) Test simple vs. bootstrap fit for producing calibration curves
   3) Produce calibration coefficients, metrics, for all sensors (batch = True)
    
"""

import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict # Counter
import re #regular expressions

#Using a fixed random seed for data sampling to ensure consistency between runs
np.random.seed(42)

#Data definitions
filename = "inputs/example_data.csv" 
out_path = "results/results.csv"     

#Regression parameters
y_column = "temp.vai" #Vaisala TMP1 precision reference sensor
n_bootstrap = 10000 #Bootstrap iterations, set 1000 for trial and debugging
test_size = 0.2 #80/20 split for training and testing

#Batch processing all the sensors? You won't see any plots.
batch = False

"""
##################### Main script starts here #################################
"""
def main():
    print(f"Looking for input data {filename}")
    try:
        df = pd.read_csv(filename)
    except Exception as e:
        print(f"Error loading CSV: {e}")
        if not os.path.exists(filename):    
            print("Input data could not be found.")
            sys.exit(1)
    print(f"Found {filename}")

    if y_column not in df.columns:
        print("Reference temperature data not found. File not valid.")
        sys.exit(1)
    else:
        print("Reference temperature data found as temp.vai")    
        print(f"Found: {len(df)} rows of data, including: ")
        print(df.head(5))
        total_groups, group_counts = count_groups_and_members(df)
        print(f"\nFound {total_groups} groups of sensors. Sensors by group:")
        for g, cnt in group_counts.items():
            print(f"g{g}.ID0 ... g{g}.ID{cnt-1}  -> {cnt} sensors")

 #If we're not running the whole batch, ask the user which sensor they want
    if not batch:
        all_ids = [select_x_column(df, y_column)]
    else:
        all_ids = [
            f"g{g}.ID{i}"
            for g in range(total_groups)
            for i in range(group_counts[g])
            ]
        
    # Split data randomly to hold-out and training sets (train and test)
    df_train, df_test = train_test_split(df, test_size)

    print(f"Training set samples: {len(df_train)}")
    print(f"Testing set samples: {len(df_test)}")
    print(f"{n_bootstrap} iterations specified.")
    print("Processing data...")

    #Isolating one column of the data to process
    y = df_train[y_column].to_numpy()
    y_test = df_test[y_column].to_numpy()
    
    """
    Here we start iterating through the list of sensors and saving
    the results to a CSV file. If no file exists, it will be created.
    """
    for x_column in all_ids:
        x = df_train[x_column].to_numpy()
        x_test = df_test[x_column].to_numpy() 
         
        # Naive fit using all the training data at once
        naive_coeffs = np.polyfit(x, y, deg=2)
              
        # Bootstrap fit with validation   
        coefficients, metrics = bootstrap_and_validate(x, y, n_bootstrap)
        mean_coeffs = np.mean(coefficients, axis=0)
        mean_metrics = np.mean(metrics, axis=0)
          
        #Calculate the difference between model outputs
        diff_models = naive_coeffs - mean_coeffs
         
        #Try the bootstrapped model against the test set
        y_pred =  mean_coeffs[0]*x_test**2 +  mean_coeffs[1]*x_test +  mean_coeffs[2]
        model_error = y_pred - y_test
         
        #compute test MAE, MSE, bias
        mae = np.mean(np.abs(model_error))
        mse = np.mean(model_error**2)
        bias = np.mean(model_error) 
        test_metrics = np.array([mae, mse, bias])
            
        #Try the naive model against the test set
        y_pred = naive_coeffs[0]*x_test**2 + naive_coeffs[1]*x_test + naive_coeffs[2]
        model_error = y_pred - y_test
            
        #compute test MAE, MSE, bias
        mae = np.mean(np.abs(model_error))
        mse = np.mean(model_error**2)
        bias = np.mean(model_error) 
        naive_test_metrics = np.array([mae, mse, bias])
        
        #Save results
        row = {
            "Sensor ID": x_column,
            "a": mean_coeffs[0],
            "b": mean_coeffs[1],
            "c": mean_coeffs[2],
            "MAE_val": mean_metrics[0],
            "MSE_val": mean_metrics[1],
            "bias_val": mean_metrics[2],
            "MAE_test": test_metrics[0],
            "MSE_test": test_metrics[1],
            "bias_test": test_metrics[2],
            "a_naive": naive_coeffs[0],
            "b_naive": naive_coeffs[1],
            "c_naive": naive_coeffs[2],
            "MAE_naive": naive_test_metrics[0],
            "MSE_naive": test_metrics[1],
            "bias_naive": naive_test_metrics[2],
            }
            
        df_out = pd.DataFrame([row])
            
        #Save the results. Append if file already exists
        write_header = not os.path.exists(out_path)
        df_out.to_csv(out_path, mode="a", header=write_header, index=False)
        print(f"\nAppended results for {x_column} to {out_path}")
    
    print("\nDone")
    """
    End of for loop
    """

    #If we are processing only one sensor, we can show the results
    if not batch:    
        np.set_printoptions(formatter={'float_kind': '{:.8f}'.format})
        print(f"\nBootstrapped {n_bootstrap} times with validation:")
        print("                           ax^2        bx          c")
        print("Mean bootstrap model :", mean_coeffs)
        print("                     :     MAE         MSE         bias")
        print("Mean validation error:", mean_metrics)
        print("Mean testing error   :", test_metrics)
        print("                           ax^2         bx          c")
        print("Naive fit model      :", naive_coeffs)    
        print("                     :     MAE         MSE         bias")
        print("Mean testing error   :", naive_test_metrics)
                
        print("\nComparing models:      ax^2         bx          c")
        print("Bootstrap mean  :", mean_coeffs)
        print("Naive fit model :", naive_coeffs)
        print("     Difference :", diff_models)
        
        #Plot the error curve of the sensor
        err = df[x_column] - df[y_column]
        plt.figure(figsize=(10,4))
        plt.plot(df[y_column], err, marker='.', linestyle='None', color='C1')
        plt.axhline(0, color='gray', linewidth=0.8)
        plt.title(f"Error plot: {x_column} - {y_column}")
        plt.xlabel("Reference temperature [C]")
        plt.ylabel("Temperature error [C]")
        plt.grid(alpha=0.3)
        plt.tight_layout()
        #plt.show()
        plt.savefig('figures/' + str(y_column), dpi = 72)
            
        #Using the validation and test sets to draw residuals
        plot_residuals(x, y, mean_coeffs, "bootstrap model validation") 
        plot_residuals(x, y, naive_coeffs, "naive model validation")
        plot_residuals(x_test, y_test, mean_coeffs, "bootstrap model test") 
        plot_residuals(x_test, y_test, naive_coeffs, "naive model test")

        
"""
####################### Main script ends here #################################

Function definitions:
"""

def count_groups_and_members(df: pd.DataFrame):
    """
    Parse how many groups and sensors are present in the batch of data.
    Each sensor group makes one complete DTP probe with 21 or 31 sensors.
    Maximum 5 x 32 = 160 sensors can be logged at once. 
    """
    # pattern: g<group>.<member>  (e.g., g0.ID0).
    pattern = re.compile(r'^g(\d+)\.(.+)$')
    groups = defaultdict(set)
    for col in df.columns:
        m = pattern.match(col)
        if m:
            group_idx = int(m.group(1))
            member_id = m.group(2)
            groups[group_idx].add(member_id)
    # summarize
    group_counts = {g: len(members) for g, members in sorted(groups.items())}
    total_groups = len(group_counts)
    return total_groups, group_counts

def select_x_column(df: pd.DataFrame, x_column: str) -> str:
    """
    Allow the user to select a sensor for the analysis
    Ensures the selected column exists and is not the Y column.
    """
    print("\nSelect sensor")
    while True:
        choice = input("Enter group and ID (e.g. g0.ID0): ").strip()
        if choice not in df.columns:
            print("Column not found. Try again.")
            continue
        if choice == x_column:
            print("Cannot compare reference to reference")
            continue
        return choice
    
def train_test_split(df: pd.DataFrame, test_size: float = 0.2):
    """
    Randomly split DataFrame into training and testing sets
    using permutation to shuffle the order of rows.
    Default split is 80/20. Return training and testing frames.  
    """ 
    indices = np.random.permutation(len(df))
    test_count = int(len(df) * test_size)
    test_idx = indices[:test_count]
    train_idx = indices[test_count:]
    df_train = df.iloc[train_idx].reset_index(drop=True)
    df_test = df.iloc[test_idx].reset_index(drop=True)
    return df_train, df_test


def bootstrap_sample_rows(x_length):
    """
    Sample random rows of rata with replacement. Return two arrays 
    of indices for model training and leftover set for validation. 
    """
    indices = np.random.randint(0, x_length, size=x_length)
    remaining_rows = np.setdiff1d(np.arange(x_length), indices, assume_unique=False)
    return indices, remaining_rows

def bootstrap_and_validate(x, y, n_bootstrap=100):
    """
    Perform bootstrap resampling and fit a quadratic model 
    (least-squares fit) for each resample. 
    Returns array of coefficients with shape (n_bootstrap, 3)
    Returns array of metrics with shape (n_bootstrap, 3)
    """
    coeffs = np.zeros((n_bootstrap, 3))
    metrics = np.zeros((n_bootstrap, 3))
    for i in range(n_bootstrap):
        
        #Generate sample and holdout indexes and split data accordingly
        sample, holdout = bootstrap_sample_rows(len(x))
        x_boot = x[sample]
        y_boot = y[sample]
        x_hold = x[holdout]
        y_hold = y[holdout]
        
        #Fit model and compute its error against the holdout set
        model = np.polyfit(x_boot, y_boot, deg=2)
        y_pred = model[0]*x_hold**2 + model[1]*x_hold + model[2]
        model_error = y_pred - y_hold
        
        #compute model MAE, MSE, bias
        mae = np.mean(np.abs(model_error))
        mse = np.mean(model_error**2)
        bias = np.mean(model_error) 
        
        metrics[i] = np.array([mae, mse, bias])
        coeffs[i] = model
    return coeffs, metrics

def plot_residuals(x, y, coeffs, modelname):
    """
    Plot residuals using the given model name and coefficients.
    """
    y_pred = coeffs[0]*x**2 + coeffs[1]*x + coeffs[2]
    residuals = y - y_pred
    plt.figure()
    plt.scatter(x, residuals, s=5)
    plt.axhline(0)
    plt.xlabel("Reference temperature [C]")
    plt.ylabel("Residual (reference - model)")
    plt.title(f"Residual Plot {modelname}")
    plt.ylim(-0.2, 0.2)
    #plt.show()
    plt.savefig('figures/' + str(modelname), dpi = 72)
       
#Note: run main only if executed as a script, not when imported
if __name__ == "__main__": 
    main()



