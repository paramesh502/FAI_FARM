# Stress Monitoring System - Technical Explanation

## Overview

The stress monitoring system continuously analyzes crop health by tracking water levels and temperature conditions across all farm cells.

---

## How It Works

### 1. Water Level Tracking

**Every Simulation Step:**

Each crop cell has a `water_level` attribute (0.0 to 1.0):

```python
# Water decreases by 0.05 per step (evaporation/consumption)
new_water_level = max(0.0, current_water_level - 0.05)
```

**Water Level Scale:**
- 1.0 = Fully watered (100%)
- 0.5 = Moderate water (50%)
- 0.3 = Low water threshold (30%)
- 0.0 = No water (0%)

---

### 2. Stress Detection Algorithm

The `get_stress_indicators()` method scans all crops:

```python
def get_stress_indicators(self):
    water_stressed = 0
    temperature_stressed = 0
    total_crops = 0
    
    # Check each crop cell
    for pos, state in self.cell_states.items():
        if state in [GROWING, HEALTHY, NEED_WATER, SOWN]:
            total_crops += 1
            attrs = self.cell_attributes[pos]
            
            # WATER STRESS CHECK
            if attrs.get('water_level', 0) < 0.3:
                water_stressed += 1
            
            # TEMPERATURE STRESS CHECK
            if temperature > 32°C AND water_level < 0.5:
                temperature_stressed += 1
    
    # Calculate percentages and health score
    return {
        'water_stressed_count': water_stressed,
        'temperature_stressed_count': temperature_stressed,
        'water_stress_percentage': (water_stressed / total_crops) * 100,
        'temperature_stress_percentage': (temperature_stressed / total_crops) * 100,
        'overall_health_score': ((total_crops - stressed) / total_crops) * 100
    }
```

---

## Stress Types

### A. Water Stress

**Condition:**
```
water_level < 0.3 (30%)
```

**What Happens:**
1. Crop is flagged as water-stressed
2. Cell may transition to `NEED_WATER` state
3. Growth progress stops
4. Master agent prioritizes watering tasks

**Example Timeline:**
```
Step 0:  water_level = 1.0  (just watered)
Step 1:  water_level = 0.95 (normal)
Step 2:  water_level = 0.90 (normal)
...
Step 14: water_level = 0.30 (threshold)
Step 15: water_level = 0.25 (WATER STRESSED!)
```

---

### B. Temperature Stress

**Condition:**
```
temperature > 32°C AND water_level < 0.5
```

**Why This Combination?**
- High temperature increases evaporation
- Low water makes crops vulnerable to heat
- Combined effect is more damaging than either alone

**What Happens:**
1. Crop is flagged as temperature-stressed
2. Increased risk of damage
3. System recommends cooling measures
4. Higher priority for irrigation

**Example Scenario:**
```
Temperature: 34°C (hot day)
Water Level: 0.4 (below 50%)
Result: TEMPERATURE STRESSED!

Temperature: 34°C (hot day)
Water Level: 0.6 (above 50%)
Result: OK (sufficient water to handle heat)
```

---

## Health Score Calculation

**Formula:**
```
overall_health_score = ((total_crops - stressed_crops) / total_crops) * 100
```

**Where:**
```
stressed_crops = water_stressed + temperature_stressed
```

**Interpretation:**
- 100% = All crops healthy
- 80-99% = Excellent condition
- 60-79% = Fair condition
- 40-59% = Poor condition
- <40% = Critical condition

**Example:**
```
Total crops: 100
Water stressed: 15
Temperature stressed: 5
Stressed total: 20

Health Score = ((100 - 20) / 100) * 100 = 80%
Status: Excellent
```

---

## Automated Recommendations

The system generates recommendations based on thresholds:

### 1. High Water Stress (>30%)
```python
if water_stress_percentage > 30:
    recommendation = "High water stress detected - Increase irrigation frequency"
```

### 2. Temperature Stress (>20%)
```python
if temperature_stress_percentage > 20:
    recommendation = "Temperature stress alert - Consider shade nets or cooling measures"
```

### 3. Rain Forecast
```python
if rain_forecast_24h:
    recommendation = "Rain forecasted - Irrigation automatically delayed to conserve water"
```

### 4. High Temperature (>32°C)
```python
if temperature > 32:
    recommendation = "High temperature warning - Monitor crops closely for heat stress"
```

### 5. Disease Risk (>5 diseased crops)
```python
if at_risk_crops > 5:
    recommendation = "Disease alert - {count} crops at risk, apply treatment"
```

---

## Integration with Agents

### Water Stress Response:

**1. Detection:**
```python
# In step_cells()
if water_level < 0.3:
    cell_state = NEED_WATER
```

**2. Task Creation:**
```python
# In master_agent.plan_tasks()
if cell_state == NEED_WATER:
    create_task(WATER, cell_position, priority=90)
```

**3. Execution:**
```python
# In watering_agent.execute_task()
water_level += 0.3  # Add water
cell_state = GROWING  # Restore state
```

### Temperature Stress Response:

**1. Detection:**
```python
# In get_stress_indicators()
if temperature > 32 and water_level < 0.5:
    temperature_stressed += 1
```

**2. Priority Adjustment:**
```python
# In master_agent.plan_tasks()
if high_temp:
    watering_priority = 95  # Increased from 90
```

**3. Dashboard Alert:**
```python
# In dashboard
if temperature_stress_percentage > 20:
    display_warning("Temperature stress alert")
```

---

## Real-Time Monitoring Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    SIMULATION STEP                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Update Weather (every 5 steps)                          │
│     - Temperature changes                                    │
│     - Humidity changes                                       │
│     - Rain forecast updates                                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Update Cell States                                       │
│     - Decrease water levels (-0.05 per step)                │
│     - Increase growth progress (+2 if water > 0.3)          │
│     - Check for state transitions                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Calculate Stress Indicators                              │
│     - Scan all crop cells                                    │
│     - Count water-stressed crops (water < 0.3)              │
│     - Count temperature-stressed crops (temp > 32 + water < 0.5) │
│     - Calculate health score                                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Generate Recommendations                                 │
│     - Check stress thresholds                                │
│     - Check weather conditions                               │
│     - Create actionable alerts                               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  5. Display in Dashboard                                     │
│     - Update stress metrics                                  │
│     - Show distribution chart                                │
│     - Display recommendations                                │
└─────────────────────────────────────────────────────────────┘
```

---

## Example Scenario

### Scenario: Hot Day with Low Water

**Initial State:**
```
Step: 50
Temperature: 28°C
Total Crops: 100
Water Levels: Various (0.2 to 0.8)
```

**Step 55: Weather Update**
```
Temperature: 33°C (increased!)
Humidity: 45%
Rain Forecast: No
```

**Step 56: Stress Detection**
```
Scanning crops...
- 25 crops with water_level < 0.3 → Water Stressed
- 15 crops with temp > 32 AND water < 0.5 → Temperature Stressed
- Total stressed: 40 crops

Calculations:
- Water Stress: 25%
- Temperature Stress: 15%
- Health Score: 60% (Fair)
```

**Step 57: Recommendations Generated**
```
1. "High water stress detected - Increase irrigation frequency"
2. "High temperature warning - Monitor crops closely"
```

**Step 58: Agent Response**
```
Master Agent:
- Creates 25 high-priority watering tasks
- Assigns to watering agent

Watering Agent:
- Executes tasks
- Waters stressed crops
- Water levels increase to 0.5+
```

**Step 65: Recovery**
```
Stress Detection:
- 5 crops still water-stressed
- 2 crops temperature-stressed
- Health Score: 93% (Excellent)

Recommendation:
- "All systems operating normally"
```

---

## Key Thresholds Summary

| Metric | Threshold | Action |
|--------|-----------|--------|
| Water Level | < 0.3 | Water stress detected |
| Temperature | > 32°C | Monitor for heat stress |
| Combined | Temp > 32 + Water < 0.5 | Temperature stress |
| Water Stress % | > 30% | Alert: Increase irrigation |
| Temp Stress % | > 20% | Alert: Cooling measures |
| Health Score | < 80% | Warning condition |
| Health Score | < 60% | Critical condition |

---

## Benefits of This System

1. **Proactive Management**
   - Detects stress before crop failure
   - Prevents yield loss

2. **Resource Optimization**
   - Targets irrigation to stressed areas
   - Avoids over-watering

3. **Real-Time Insights**
   - Continuous monitoring
   - Immediate alerts

4. **Data-Driven Decisions**
   - Quantified stress levels
   - Actionable recommendations

5. **Automated Response**
   - Agents respond to stress automatically
   - Reduces manual intervention

---

## Future Enhancements

Potential improvements:

1. **Nutrient Stress**
   - Monitor soil nitrogen, phosphorus, potassium
   - Detect nutrient deficiencies

2. **Disease Stress**
   - Track disease progression
   - Predict outbreak risk

3. **Pest Stress**
   - Monitor pest populations
   - Detect infestation early

4. **Soil Stress**
   - Track soil compaction
   - Monitor pH levels

5. **Historical Analysis**
   - Track stress patterns over time
   - Predict seasonal stress periods

---

*This stress monitoring system provides comprehensive crop health management through continuous monitoring, intelligent detection, and automated response.*
