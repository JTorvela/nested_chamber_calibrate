# nested_chamber_calibrate

**Author:** Janne Erik Torvela  
**Contact:** janne.torvela@oulu.fi
**Organization:** University of Oulu / Oulun Yliopisto
**Website:** https://github.com/JTorvela/nested_chamber_calibrate

## Project Overview
Batch calibration analysis of DS18B20 temperature sensors.

**This project repository contains a set of measured data for a batch of DS18B20 type temperature sensors and an example script for the process of deriving the calibration function for each sensor. At default, the script identifies and lists the sensors by group and ID number, in the format "g_.ID_". To select a sensor  for analysis, run the script and type in e.g. "g1.ID5". To process the entire set of sensors at once, change "batch = True" in the code.**

The error characteristic of a DS18B20 digital temperature sensors is described by the manufacturer as a second order curve (Maxim Integrated 2002). To compensate for the error, we need to find the calibration function coefficients ax + bx^2 + c for each sensor. Since the output of the sensor is not continuously variable but quantized in increments of 0.0625 C (Maxim Integrated 2019), sensor noise and other variations cause each sensor to switch randomly between two or more values and the resulting distribution does not fall neatly around a mean. This statistical property may cause biases when fitting a regresson model for the calibration function coefficients. 

A simple regression fit and validation would be done by splitting the data into training and hold-out sets, usually in a 80:20 ratio. The regression model is fitted to the training set and the model predictions are tested with the hold-out set which the model has not seen. Here, instead of directly fitting the model, a distribution-independent resampling method known as bootstrapping may be used to assess the real properties of the distribution underlying the sample. This method involves selecting a random sample of the training data, fitting the regression model to the selection, and validating the model against the data which was not randomly selected previously, repeating many times. The average regression model is then used and tested against the hold-out set as before. (Efron 1979; Davison 1997). In the example script, a comparison is made between a bootstrapped model and naive model fitting without resampling to see whether the bootstrapping method is necessary for useful results.

To make sure the sampled data itself is valid, an isolated enclosure should be used to stabilize the temperature between the sensors (Elyounsi, Kalashnikov 2021). This was done by placing the batch of sensors and a precision reference thermometer inside a box made of foam insulation. Small computer fans were used for mixing the interior air continuously to transfer heat between the sensors. A large and heavy aluminium heatsink with the radiating fins exposed to the outside of the box was used to exchange heat with the environment and to slow down temperature fluctuations. The box was then placed inside an environmental simulation chamber and cycled from -40 C to +40 C in discrete steps over two days with continuous logging of data every five seconds from all sensors. The temperature was allowed to stabilize for two hours at each step. This nested chamber design was chosen to minimize the effect of thermostat hysteresis causing small temperature fluctuations in the outer chamber. 


References:

Elyounsi A., Kalashnikov A.N., 2021, Evaluating Suitability of a DS18B20 Temperature Sensor for Use in an Accurate Air Temperature Distribution Measurement Network. Eng. Proc. 2021, 10, 56. https://doi.org/10.3390/ecsa-8-11277 

Maxim Integrated Products Inc., 2019, Programmable Resolution 1-Wire Digital Thermometer, https://www.analog.com/media/en/technical-documentation/data-sheets/DS18B20.pdf (accessed 30.1.2026)

Maxim Integrated Products Inc., 2002, Application note 208. Curve Fitting the Error of a Bandgap-Based Digital Temperature Sensor, https://www.analog.com/en/resources/technical-articles/curve-fitting-the-error-of-a-bandgapbased-digital-temperature-sensor.html (accessed 30.1.2026)

Davison A.C., Hinkley D.V., 1997, Bootstrap Methods and their Application. Cambridge: Cambridge University Press (Cambridge Series in Statistical and Probabilistic Mathematics). 

Efron B, 1979, Bootstrap Methods: Another Look at the Jackknife, The Annals of Statistics, Ann. Statist. 7(1), 1-26, (January), DOI: 10.1214/aos/1176344552

## Data Sources

Example data is provided in the folder "inputs".

### Inputs folder

The file "example_data.csv" contains a cleaned data log of the precision reference sensor and 135 individual DS18B20 sensors in the batch with 5 second sampling interval. The raw data was manually trimmed to include the steady state temperature after each temperature step. 

## Methods Summary

**Model Framework:** 
1) Read CSV data file
2) Split data into training and testing sets with 80/20 split using a random permutation
3) From the training data, select randomly with replacement and separate non-selected samples for validation later. 
4) Fit regression model to the randomly selected samples.
5) Test fit against non-selected samples.
6) Repeat steps 3-5 for N times
7) Compute the mean regression model and validation results from steps 3-6 (mean bootstrap model, validation metrics)
8) Try the mean bootstrap model against testing set
9) Fit regression model directly on training set
10) Try direct regression model against testing set
11) Save resulting models and all metrics to CSV output file


## Repository Structure

| Folder/File | Description |
|-------------|-------------|
| inputs/ | Example data set |
| results/ | Saved model outputs |
| figures/ | Saved figures for individual sensor tests (not batch operation) |
| process_data.py | main process script |
| environment.yml | Conda environment from Spyder 6 |
| CITATION.cff | Citation metadata, sourced directly from Zenodo |

## How to Reproduce

### Computational requirements
Not critical. 
Note: if you set batch = True in the script, bootstrapping with 10,000 iterations for 135 sensors may take an hour or two. 

### Environment
Developed in Spyder 6. If needed, run: 
```bash
conda env create -f environment.yml
conda activate nested_chamber_calibrate
```

### Run the code
```bash
python process_data.py
```
## Results

[Error plot before calibration](figures/example_error.png)

[Residual error plot after calibration (naive model fitting)](figures/example_residual.png)

## Citation

If you use this software, please cite:

**APA format**

Janne Erik Torvela (2026).
*nested_chamber_calibrate* (Version 0.1.0).
University of Oulu.
DOI: dummy.url

**BibTeX**

```bibtex
@software testproject,
  author = Janne Erik Torvela,
  title = nested_chamber_calibrate,
  year = 2026,
  version = 0.1.0,
  doi = dummy.url,
  url = https://github.com/JTorvela/nested_chamber_calibrate
}
```
or

[![DOI](https://zenodo.org/badge/DOI/DOI_PENDING.svg)](DOI_PENDING)

## License

CC-BY-4.0

## Contribution Guidelines
Contributions that improve the quality, clarity, and reproducibility of this project are welcome.
* Open an issue before making major or result-affecting changes.
* Keep pull requests focused and clearly describe what changed and why.
* Follow existing code style and update documentation as needed.
* Do not modify code or data used to reproduce published results without discussion.
* Ensure workflows remain reproducible (environment, dependencies, random seeds).
* Do not commit large or restricted datasets; respect data licenses.
By contributing, you agree that your work will be released under the project’s license.

