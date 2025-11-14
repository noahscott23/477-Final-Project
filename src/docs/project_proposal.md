Team Members: Megan Fung, Noah Scott, Archie Phyo  
Course: Information Visualization– CSC-477-01-2258  
Assignment: Project Proposal 

## **Topic (Socially/ Scientific Significant):** 

→ Climate Change \+ Projected Sea Level Rise: Visualizing the Future of Coastal Cities

- Rising seas threaten over 600 million people living in coastal zones worldwide, making this an urgent environmental and humanitarian issue  
- Background Knowledge:   
  - Global Climate Change causes Sea Level Rise (ice sheets melting \+ ocean temperatures warm)  
  - Result of Sea Level Rise: coastal populations experience floods, infrastructure damage, etc. 

→ For this project, our group will visual both global trends and localized impacts of sea level rise 

## **Goal (What are we trying to convey?):** 

→ Create an interactive visualization to illustrate how projected sea levels: 

- Change under different greenhouse gas emissions   
- Will impact coastal regions and populations

→ Our visualization aims to:

- Clearly communicate trends in global \+ regional sea level rise over time  
- Allow for scenario comparison (different emission levels) to highlight the effect of mitigation  
- Enable exploration of regional projections for coastal cities

→ Overall, our project’s goal is to translate complex climate change data into an interactive explorable story that informs and motivates awareness

## **Audience:** 

→ General public (students, policy makers, environmentalist, those concert with environmental change)

- Why would this audience engage with the visualization?   
  - Interactive visual allows audience to explore “what if” scenarios   
  - Dynamic comparison of future/ present, regional differences, etc.   
- Assumptions the audience must have?   
  - Audience has no prior knowledge about how climate change affects sea levels 

## **Dataset(s):** 

→ We will be using datasets from NASA’s sea level change portal based on the IPCC sixth assessment report projections. These datasets are authoritative, peer reviewed, and maintained by the NASA Jet Propulsion Lab. The datasets below provide projections of global and regional sea level change from 2020-2150. 

- [NASA: Sea Level Projections from the IPCC 6th Assessment Report](https://github.com/podaac/ipcc-ar6.git)   
- git repo– Data/ipcc\_ar6\_sea\_level\_projection\_psmsl\_id\_24.xlsx  
- [https://sealevel.nasa.gov/data\_tools/17](https://sealevel.nasa.gov/data_tools/17)  
- [https://www.earthdata.nasa.gov/topics/climate-indicators/sea-level-rise](https://www.earthdata.nasa.gov/topics/climate-indicators/sea-level-rise)  
- [https://ipcc-browser.ipcc-data.org/browser/dataset/8441](https://ipcc-browser.ipcc-data.org/browser/dataset/8441)  
- [https://sealevel.nasa.gov/task-force-scenario-tool](https://sealevel.nasa.gov/task-force-scenario-tool)


## **Questions to Answer with Data:** 

→ How much will global and regional sea levels rise by the year 2100, under different emission scenarios?   
→ Which coastal cities are the most vulnerable to extreme sea level events? How does vulnerability vary geographically and in respect to emissions trajectory?   
→ How do mitigation scenarios alter the timing or severity of impacts for different regions?

## **Sketches:**  

Visualization Description: 
An interactive world map visualization designed to communicate how rising sea levels will affect major coastal cities. The interface should be a world map with key cities highlighted as colored points. Each poit represents a coastal city included in the dataset and color encodes its risk level from projected sea level (e.g low, moderate, high). 
The visualization should include a color legend, showing the three risk categories and corresponding colors. 
The visualization should have either a toggle or filter system, allowing users to switch on and off different risk levels to isolate specific groups of cities. 
The visualization should also have a hover tooltip that appears when a user hovers over a city. The tooltip should display key information such as population, eleveation, projected sea level rise by 2050 or 2100, and the city's risk classification. 
Overall, the visualization aims to lay out core ideas behind an interactive map that allows users to visually explore global and regional impacts of sea level rise, compare risk levels across cities, and understand how vulnerability changes over time. 
→ Interactivity: 

- Hover Tooltip: shows specific projections per coastal region   
  - City name, project sea level, risk category, population at risk  
- Time Slider (2020-2100): analyze rising sea levels over time   
- Risk Level Filter: isolate cities based on risk level or region  
- Color Intensity: risk level 


Sketch 2 Description: 
**TODO**
→ Interactivity: 

- Hover Tooltip: shows precise values on curve   
  - Year, sea level, rate of change, notable events   
- Vertical Time Market: draggable vertical line, with a tooltip that updates the current value on the curve   
- Scenario Toggle: user selection for different emission scenarios and how they affect sea level projections 

## 

## **Success Metrics:** 

- Clarity and Interactivity:   
  - test visualization with individuals with no technical knowledge to ensure the story is understandable  
  - Evaluate user experience (exploring toggles, sliders, filters, hover interactions, etc.)   
- Accuracy: verify all data values and projects against cited sources   
- Design Choices/ Visual Encodings: ensure alignment with best practices in visualizations taught in class  
- Conduct short user tests with other classmates to confirm clarity
