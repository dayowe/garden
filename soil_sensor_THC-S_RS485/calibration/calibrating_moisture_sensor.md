This guide provides a clear methodology for calibrating moisture sensors specifically for coco coir substrates. It outlines detailed steps to achieve accurate volumetric water content readings, ensuring precise irrigation management for optimal plant growth. Follow this guide to systematically calibrate your sensors and enhance the reliability of your moisture monitoring system.

## Step 1: Collect Empirical Data

#### 1.1 Dehydrate Coco Coir Samples
**Planning**

Decide on what volume to use for the calibration and make sure you have a way to collect that amount. I designed [a specialized container](https://www.thingiverse.com/thing:6556448) to help collect exactly the amount I want in a reproducible way. Weigh the container that will hold your substrate sample and record the empty weight as 'container weight'.

**Selection**

Choose a sample that is representative of the medium you will be measuring in real scenarios. The samples should be of uniform texture and composition to reduce variability. Consistency in texture and composition is crucial for maintaining the validity of the process. Weigh the sample you took and record it as 'initial substrate sample weight + container weight'. subtract 'container weight' from this and record the value as 'initial substrate sample weight'.

**Preparation**

Begin by drying your substrate sample at 105°C in the oven. When using a different container for the drying in the oven, make a note of its weight. The drying process can take about 24-48h. Stirring the coco every once in a while and weigh the container to get an an idea of how much water evaporated (for reference, 1 gallon of bone-dry Canna Coco Professional Plus weights about 330g). Once the weight of the coco stopped decreasing, the coco is fully dehydrated. subtract the 'drying container weight' from the total weight and record this as 'dry substrate weight'. Also subtract the dry weight from 'moist sample weight' and record this as the 'initial water content'.

**Conditioning**

Rehydrate the dry substrate by adding a bit more than the amount of water it held initially. Mix very well. Now fill your pot with the rehydrated substrate in layers and compact the substrate gently after each layer. Once you reached the level at which the soil sensor will sit, insert the sensor into the pot and compact the substrate in the same way as the other layers, to make sure the sensor probes make good contact with the substrate. Once the container is packed fully, you are ready to position the container in your setup and get ready to saturate the sample.

**Some considerations**
  
Ideally the pot does not need to be touched anymore for the entire duration of the calibration, to avoid any movement of the probes. 
  
An AC-powered scale is beneficial for continuously monitoring water evaporation, as it does not require battery changes, ensuring uninterrupted data collection. 
  
Since salinity can influence water retention and sensor readings, it's vital to calibrate your sensor, taking into account the typical salinity levels of your coco coir.
  
A spreadsheet template that includes a lot of helpful formulas.is available [here](https://docs.google.com/spreadsheets/d/1qk80CA_TloXIW8XoP4QbN24SspkzT8rVAmU1Bg_5XQ4).

#### 1.2 Log and Measure Wet Weight

**Initial Weighting**

Gradually water the substrate until runoff occurs, using a pressure sprayer to ensure even distribution. Begin by determining an approximate capacity for your substrate and water your container incrementally, utilizing about 5% of the total volume per addition to achieve uniform saturation (as a reference my collected 1 gallon sample could hold a maximum of about 2L of water). As you approach the substrate's estimated water-holding capacity, reduce the volume of each addition and look for the initial signs of runoff. Upon noticing runoff, document the raw measurement and the weight on your sheet; this marks your saturation point and establishes a baseline. This is the beginning of the drying phase.

#### 1.3 Dry and Dehydrate Coco Coir
This step involves systematically removing moisture from the coco coir. Let the coco coir naturally dry to different extents and repeat the weighing and sensor reading process at various stages. 

#### 1.4 Organization and Recording

**Data Management**: Arrange your data to reflect the decremental moisture levels, documenting the exact amount of water evaporated, subsequent weights, and sensor readings in an organized manner.

**Notes on Environmental Conditions**: Document any changes in ambient temperature and humidity, as these could influence sensor performance compared to your initial calibration data.

**Drying Process**: To simulate drying conditions, you might let the coco coir naturally dry to different extents and repeat the weighing and sensor reading process at various stages. 

## Step 2: Calculate True VWC

#### 2.1 Understanding VWC

**Volumetric Water Content (VWC)** is a measure that indicates the volume of water per unit volume of soil (or, in this case, coco coir). It is typically expressed as a percentage. This measure is essential for understanding the water-holding capacity of the coco coir and how this relates to plant water needs.

#### 2.2 Calculation Method

1. **Direct Volume Measurement**:

   If you've measured water by volume (e.g., using a measuring cup or a graduated cylinder), you're directly adding known volumes of water to the coco coir.
   
   The calculation is straightforward:
  
     <p class="equation"><center><img alt-text="svg/vwc_equation" src="https://raw.githubusercontent.com/dayowe/garden/master/soil_sensor_THC-S_RS485/calibration/svg/vwc_equation.svg"></center></p>

     <!--
     \text{VWC ()} = \frac{\text{Volume of water added (L, ml, or any consistent unit)}}{\text{Volume of coco coir (same units)}} \times 100
     -->
  
2. **Conversion from Weight to Volume**

   Often, water is added based on weight, assuming the well-established density of water of approximately 1 g/cm³ (or 1 kg/L). This means 1 gram of water corresponds to 1 cubic centimeter (cm³) of volume.
   
   If you’ve recorded the weight of water added, convert this weight to volume for the VWC calculation (especially important if the volume of coco coir is known in cubic centimeters or liters).
     
     Volume of water added = Weight of water added (g), since 1 g of water = 1 cm³ of water.
     
     Use the converted volume in the VWC calculation formula as above.

#### 2.3 Deriving the Volume of Coco Coir

The volume of coco coir could be known directly if you’ve used a container with a defined volume for the experiments. However, if not directly known, you might need to measure or calculate this based on the dimensions of the container or space where the coco coir is contained.

#### 2.4 Iterative Additions and Calculations

Throughout the saturation and drying process, as you incrementally add or lose water, it’s critical to account for each step’s specific added (or evaporated) water volume in your VWC calculations.

For each specific condition (i.e., after each addition or drying phase), a new VWC calculation gives you data points across a range of moisture levels within the coco coir.

#### 2.5 Recording and Reflection

**Data Accuracy**: Ensure your measurements (both volume and weight) are as accurate as possible to improve the reliability of your VWC calculations. Small inaccuracies can lead to significant deviations when scaling up or applying the results to practical scenarios.

**Comprehensive Data Collection**: To build a robust calibration curve later, collect a wide range of data points covering from near-dry to fully saturated conditions of the coco coir.

## Step 3: Plot Data

#### 3.1 Preparing Your Data

Before plotting, ensure all your data is systematically organized. Typically, this means having a table where each row represents a different state of moisture content in your coco coir, marked by:
  - The volume of water added (or weight, if you have converted it to volume),
  - The corresponding sensor readings obtained post-distribution of water,
  - The calculated true VWC (%) for each condition.

#### 3.2 Choosing the Right Software

Select a software tool that is capable of handling scatter plots and can perform regression analysis. Excel is user-friendly for those familiar with spreadsheets, while MATLAB and Python (using libraries like Matplotlib or Seaborn for plotting and Pandas for data manipulation) offer more power and flexibility for data analysis.

#### 3.3 Plotting

1. **Input Data**:
   
   Import or enter your organized data into the chosen software.
   
   Specifically, you will use:
     - The sensor readings for the X-axis,
     - The calculated true VWC (%) for the Y-axis.

1. **Creating Scatter Plot**:
   
   Use the software's plotting function to create a scatter plot. This visually represents each paired observation of your empirical data as a point in two-dimensional space, with the moisture sensor's raw readings plotted against the corresponding true VWC values.

2. **Labeling and Customization**:
   
   Clearly label your X-axis (Sensor Readings) and Y-axis (True VWC %) and provide an appropriate title for your graph.
   
   Customize your plot for better clarity and presentation, adjusting elements like scales, point styles, and colors as necessary. Clarity in the plot aids in better interpretation and analysis.

#### 3.4 Initial Observation

**Identify Patterns**: Initially observe the spread and pattern of the plotted points. In many cases, the relationship between sensor readings and moisture content will not be perfectly linear, particularly with complex substrates like coco coir, which may exhibit different water retention properties at different saturation levels.

**Outliers**: Look for any points that deviate significantly from the overall pattern. These outliers could indicate measurement errors or anomalies in sample preparation.

#### 3.5 Why Plotting Is Crucial

**Visual Representation**: It helps in visually assessing the relationship between the sensor readings and true VWC. Trends, linearity or non-linearity, and potential outliers become easily discernible.

**Basis for Regression Analysis**: A plotted graph is instrumental in determining whether a linear, polynomial, or some other form of regression is most appropriate for modeling the relationship between your variables.

**Communication and Validation**: Graphical representation of your findings is indispensable for effectively communicating your research outcomes and for further validation steps.

## Step 4: Create Calibration Curve

#### 4.1 Understanding the Calibration Curve

A calibration curve serves as a graphical representation that maps sensor readings to known values of true volumetric water content (VWC). This step is vital because it transforms raw data into a functional relationship, expressed mathematically, that can be used to interpret unknown samples accurately.

#### 4.2 Quadratic Regression Analysis

**Rationale for Quadratic Regression**: Coco coir, like other growing mediums, might not exhibit a linear relationship between sensor readings and moisture content across the full range of moisture levels. A quadratic curve, which is essentially a polynomial of degree two, can often more accurately model the non-linear behavior observed in the data.
  
**Application**:
  1. Input your plotted data points (true VWC % vs. sensor readings) into your chosen software capable of regression analysis.
  
  2. Select a quadratic regression analysis tool within the software. The goal is to fit a curve that best represents the plotted data points, minimizing the difference (or error) between the actual data points and the values predicted by the curve.

  3. The software will output a quadratic equation in the form of:
     
     **y = ax² + bx + c**
     
     - Here, **y** is the calculated true VWC (%),
     - **x** is the sensor reading,
     - **a**, **b**, and **c** are the coefficients determined by the regression analysis.

#### 4.3 Interpreting the Coefficients

**Coefficients (a, b, c)**: These values are key to understanding the shape and position of your calibration curve. They adjust the curve’s direction (upwards or downwards), its steepness, and where it intersects the Y-axis. The accuracy of these coefficients directly impacts the precision of moisture readings in your coco coir.

#### 4.4 Confidence and Fit

**Goodness-of-Fit**: Evaluate the fit of your quadratic curve. Software tools often provide R² (R-squared), a statistical measure that represents the proportion of the variance for the dependent variable (true VWC) that's predicted from the independent variable (sensor reading). An R² value closer to 1 indicates a better fit.
  
**Residuals Analysis**: Examine the residuals, which are the differences between observed values (the actual true VWC %) and the values predicted by your regression model. A pattern in the residuals may suggest that a different model might better fit your data, or it might highlight outliers or other data issues.

#### 4.5 Visualization

Plotting the calibration curve on top of your empirical data points visually validates how well the curve fits the data. Adjustments to the logging method, measurements, or the range of data points might be necessary for optimizing this fit.

#### 4.6 Application

Once the coefficients **a**, **b**, and **c** are determined, your calibration curve is ready. This quadratic equation becomes a powerful tool for interpreting raw sensor readings from your coco coir substrate into actionable VWC percentages.

This curve should be validated periodically with new data, ensuring its accuracy over time and considering any potential changes in the coco coir's characteristics or the sensing environment.

## Step 5: Derive the Formula

#### 5.1 From Coefficients to Calibration Curve

Having applied quadratic regression analysis in the previous step, you now have three coefficients: **a**, **b**, and **c**. These coefficients define the shape and orientation of your calibration curve, which mathematically models the relationship between the sensor's raw VWC readings and the true VWC percentages in coco coir.

#### 5.2 The Quadratic Formula

The general form of the quadratic equation you have derived is:

<p class="equation"><center><img alt-text="svg/true_vwc_equation.svg" src="https://raw.githubusercontent.com/dayowe/garden/master/soil_sensor_THC-S_RS485/calibration/svg/true_vwc_equation.svg"><center></p>

<!--
True VWC (%) = \( a \times (\text{Sensor Reading})^2 + b \times \text{Sensor Reading} + c \)
-->

**a** (quadratic coefficient): Influences the curvature of the model. The presence of this term allows the model to fit a wider range of nonlinear behaviors, which is crucial for accurately capturing the moisture characteristics of coco coir across different saturation levels.

**b** (linear coefficient): Controls the slope of the curve. This term linearly scales the sensor readings, adjusting for proportionality between the readings and the true moisture content.

**c** (constant term): Represents the y-intercept of the curve. It corrects for any baseline offset in sensor readings, ensuring accuracy even at low moisture levels.

#### 5.3 Constructing the Formula

1. **Input the Coefficients**: Substitute the specific values of **a**, **b**, and **c** obtained from your regression analysis into the quadratic formula.

2. **Formula Simplification**: While the general form remains constant, the actual numerical values of your coefficients will produce a unique calibration curve tailored to your specific sensor and coco coir setup. Simplifying the formula by rounding coefficients to sensible numbers of decimal places can help in practical applications, but always ensure to maintain the formula's accuracy.

#### 5.4 Utilizing the Calibration Formula

**Predicting True VWC**: With the calibration formula established, you can now input raw sensor readings into this formula to calculate the corresponding True VWC % in your coco coir. This process transforms raw data into actionable insights, guiding irrigation and care in your hydroponic or soilless systems.

#### Example

Suppose the quadratic regression provided the coefficients as follows:

<p class="equation"><center>**a** = 0.005, **b** = -0.01, and **c** = 25.</center></p>

Your specific calibration formula would then be:

<p class="equation"><center><img alt-text="svg/true_vwc_equation_example.svg" src="https://raw.githubusercontent.com/dayowe/garden/master/soil_sensor_THC-S_RS485/calibration/svg/true_vwc_equation_example.svg"></center></p>

<!-- 
True VWC (%) = 0.005 \times (\text{Sensor Reading})^2 - 0.01 \times \text{Sensor Reading} + 25
-->

#### 5.5 Validation and Adjustment:

After deriving your formula, it's essential to test its accuracy with new, unseen coco coir samples and sensor readings. Compare predicted VWC values against actual measurements obtained via the weight/volume method described in earlier steps.

If discrepancies arise, review your empirical data, regression analysis, and any potential sources of error in measurements. Adjustments to the calibration formula or additional data collection might be necessary for optimization.

#### 5.6 Why It Matters

This step distills your empirical observations and analysis into a tangible tool, the calibration formula. It's this formula that directly influences your ability to manage plant hydration effectively, demonstrating the vital bridge between theory and practical application in precision agriculture practices, particularly when working with challenging substrates like coco coir.

## Step 6: Validate the Calibration

#### 6.1 Preparation for Validation

**Collect New Samples**: To validate your formula, begin with fresh samples of coco coir not previously used in the calibration process. This ensures that your validation tests the formula's applicability to a broad range of conditions, not just the ones it was derived from.

**Ensure Uniformity**: Just as in the initial data collection, ensure these samples are uniform in composition and have been dried to baseline conditions to start on equal footing.

#### 6.2 Conducting Validation Tests

1. **Rehydration Cycles**: Sequentially add known volumes of water to the new coco coir samples. After each addition, allow for thorough water distribution within the samples before taking sensor readings. This step mirrors the initial data collection process but now tests the formula's predictions against actual conditions.
   
2. **Apply the Calibration Formula**: For each new sensor reading obtained, apply the derived calibration formula to predict the sample's VWC.

3. **Measure Actual VWC**: Concurrently, calculate the actual VWC for these samples using the weight/volume method (as outlined in Step 2) to have a baseline for comparison.

#### 6.3 Comparing Predicted vs. Actual VWC

**Analyze the Differences**: For each sample, compare the VWC predicted by your calibration formula against the actual VWC calculated. Note the discrepancies and assess the formula's precision.

**Statistical Analysis**: Employ statistical tools to quantify the accuracy and reliability of your formula. Techniques such as calculating the mean absolute error (MAE) or root mean square error (RMSE) can provide insights into the formula's overall performance.

#### 6.4 Adjustments Based on Validation

**Refinement of the Formula**: If significant discrepancies are observed, you may need to adjust the calibration curve. This could involve collecting additional data points to refine the coefficients or reevaluating the regression analysis approach.

**Consider Environmental Variables**: If external factors like temperature or humidity significantly affect your sensor's performance, consider incorporating these variables into your calibration model or formula.

#### 6.5 Finalization

Once you've adjusted the calibration formula and the validation tests show a high degree of accuracy, the formula can be considered validated. However, periodic revalidation is recommended, especially if the conditions of use change or as part of routine quality control.

#### 6.6 Why Validation Matters

Validation is not merely a procedural step but a foundational component that ensures the reliability of your calibration formula. It's what transforms your calibration from a theoretical model into a practical tool for precise moisture management in coco coir. Proper validation:

**Builds Confidence**: Demonstrates that the formula works under varied conditions and can be trusted for making decisions in real-world applications.

**Ensures Accuracy**: Identifies and corrects any discrepancies, ensuring that the formula accurately reflects the moisture content in coco coir, which is crucial for optimizing plant growth conditions.

#### 6.7 Repeatability

Repeatability concerns the consistency with which your calibration process can be replicated, yielding similar results under the same conditions. This is a measure of the reliability of your calibration formula across multiple trials and is pivotal for ensuring that your moisture measurements can be trusted over time.

**Multiple Trials**: Conduct the calibration process several times, using different samples of coco coir. Consistent results across these trials enhance confidence in the formula's reliability.
  
**Controlled Conditions**: Ensure that each trial is conducted under similar environmental conditions and with coco coir of comparable characteristics to minimize variables that could lead to inconsistency.
  
**Protocol Documentation**: Documenting each step in the calibration process meticulously allows for precise repetition. This record-keeping aids in identifying any steps that may contribute to variability in results.

#### 6.8 Sensitivity

The sensitivity of your moisture sensor pertains to its ability to detect small changes in the moisture content of coco coir. Given the varied water-holding characteristics of coco coir and its importance in regulating plant hydration, a sensor's sensitivity is crucial for fine-tuning irrigation strategies.

**Range of Detection**: Confirm that the sensor provides accurate readings across the full moisture spectrum expected in coco coir, from dry to fully saturated.
  
**Minor Variations**: Assess how well the sensor can discern slight variations in moisture content, as these nuances can be critical for plant health.

#### 6.9 Environmental Factors

The calibration process and subsequent VWC measurements can be influenced by environmental conditions such as temperature and salinity. Both factors can affect sensor readings and the physical properties of coco coir, making it essential to consider these in your calibration formula.

**Temperature**: Temperature fluctuations can impact sensor responsiveness and the evaporation rate of water from coco coir. If your growing environment experiences significant temperature changes, consider calibrating your sensor across a range of temperatures to encompass these variations.
  
**Salinity**: Coco coir's salinity can change depending on source and treatment. Since salinity can influence water retention and sensor readings, it's vital to calibrate your sensor, taking into account the typical salinity levels of your coco coir.
  
**Adjusting for Environmental Factors**: If environmental factors significantly impact sensor readings, you might need to develop a more complex calibration model. This model could include variables for temperature and salinity, allowing for adjustments to the VWC formula based on current environmental conditions.

### Final Thoughts

Considering repeatability, sensitivity, and environmental factors in your calibration process ensures that you develop a precise and reliable formula for measuring true VWC in coco coir. This meticulous approach enhances the validity of your moisture management strategy, optimizing irrigation and nutrient delivery for plant health in hydroponic or soilless systems. By addressing these considerations, you can mitigate potential sources of error and variability, leading to more accurate and consistent moisture monitoring.