# nested_chamber_calibrate

**Author:** Janne Erik Torvela  
**Contact:** janne.torvela@oulu.fi
**Organization:** University of Oulu / Oulun Yliopisto
**Website:** https://github.com/JTorvela/nested_chamber_calibrate

## Project Overview
Batch calibration analysis of DS18B20 temperature sensors.

The error characteristic of a DS18B20 digital temperature sensors is described by the manufacturer as a second order curve (Maxim Integrated 2002). To compensate for the error, we need to find a closely fitting second order function described by its coefficients ax + bx^2 + c for each sensor. Since the temperature measured by the sensor is not continuously variable but quantized to a resolution of 0.0625 C at the full resolution of the sensor (Maxim Integrated 2019), inherent sensor noise and system variations cause each sensor sample to switch randomly between discrete values and the resulting distribution does not fall neatly around a mean. This statistical property may cause biases with simple regresson model fitting. 

A distribution-independent resampling method known as bootstrapping is used to assess the properties of the distribution underlying the sample. This method involves randomly selecting a portion of the data, fitting the regression model of the calibration function to the selection, and testing the model against the remaining data, repeatedly for thousands of times. The mean of the regression model results can then be used for the final calibration function. (Efron 1979; Davison 1997). In the example script, a comparison is made between a bootstrapped model and directly fitting a regression model to the available data without resampling, using an 80/20 split between model training and validation. This comparison is made to determine whether the bootstrapping method is necessary for useful results. 

To ensure that the comparisons between a reference sensor and the sensors being calibrated are valid, we must ensure that all sensors have stabilized to the same temperature inside an isolated enclosure (Elyounsi, Kalashnikov 2021). This was accomplished by placing the batch of sensors inside an insulated box with a large thermal mass in the form of a heavy aluminium heatsink with radiating fins. Small computer fans provide sufficient mixing and transfer of heat within the insulated container. The fins of the aluminium heatsink are exposed to the outside of the box, enabling heat exchange with the environment. The box was then placed inside an environmental simulation chamber and cycled between -40 C and +40 C in discrete steps over two days with continuous uninterrupted logging of data from all sensors. This nested chamber design diminishes the effect of thermostat hysteresis of the environmental simulation chamber. The reference sensor is a Vaisala TMP-1 platinum resistance sensor calibrated to a certified accuracy better than +/- 0.01 C over the measured temperature range. The system was allowed to stabilize for two hours at each temperature, and 400 points of data were manually selected from each step. 

This project repository contains a set of measured data for a single batch of DS18B20 type temperature sensors and an example script for the process of deriving the calibration functions for each sensor.  

References:

Elyounsi A., Kalashnikov A.N., 2021, Evaluating Suitability of a DS18B20 Temperature Sensor for Use in an Accurate Air Temperature Distribution Measurement Network. Eng. Proc. 2021, 10, 56. https://doi.org/10.3390/ecsa-8-11277 

Maxim Integrated Products Inc., 2019, Programmable Resolution 1-Wire Digital Thermometer, https://www.analog.com/media/en/technical-documentation/data-sheets/DS18B20.pdf (accessed 30.1.2026)

Maxim Integrated Products Inc., 2002, Application note 208. Curve Fitting the Error of a Bandgap-Based Digital Temperature Sensor, https://www.analog.com/en/resources/technical-articles/curve-fitting-the-error-of-a-bandgapbased-digital-temperature-sensor.html (accessed 30.1.2026)

Davison A.C., Hinkley D.V., 1997, Bootstrap Methods and their Application. Cambridge: Cambridge University Press (Cambridge Series in Statistical and Probabilistic Mathematics). 

Efron B, 1979, Bootstrap Methods: Another Look at the Jackknife, The Annals of Statistics, Ann. Statist. 7(1), 1-26, (January), DOI: 10.1214/aos/1176344552

## Data Sources

Example data is provided in the folder "inputs".

### Inputs folder

The file "example_data.csv" contains a cleaned data log of the reference sensor and 135 individual DS18B20 sensors in the batch with 5 second sampling interval. The raw data was manually trimmed to include the steady state temperature after each temperature step. 

## Methods Summary

**Model Framework:** 
1) Read CSV data file
2) Split data into training and testing sets with 80/20 split using a random permutation
3) From the training data set, randomly select 400 samples (can be duplicates) and separate non-selected samples
4) Fit regression model to the selected samples.
5) Test fit against non-selected samples
6) Repeat steps 3-5 for N times
7) Compute the mean of regression models and test results from steps 3-6 (mean bootstrap model)
8) Try the mean bootstrap model against testing set
9) Fit regression model directly on training set
10) Try direct regression model against testing set
11) Save both models and testing results


## Repository Structure

| Folder/File | Description |
|-------------|-------------|
| notebooks/ | SE1–SE4 notebooks |
| inputs/ | minimal input data required, note most data should be stored on OGC/FAIR compliant databases and accessed from stable URLs |
| ../raw_data/ | data downloaded from stable URLs/PDIs |
| ../processed_data/ | analysis-ready datasets |
| model_data/ | Saved model outputs, model configuration files, predictions|
| figures/ | Figures, tables, graphs, and data-derivatives (e.g. summary statistics) displayed in manuscript text |
| run_reproducibility.py | Reproducibility wrapper |
| Dockerfile | Reproducible container |
| CITATION.cff | Citation metadata, sourced directly from Zenodo |

## How to Reproduce

### Computational requirements
Not critical. 

### Data access configurations
NA

### Run the code
```bash
pip install -r requirements.txt
python run_reproducibility.py
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

