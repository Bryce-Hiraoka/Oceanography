from flask import Flask, render_template, request, redirect, url_for
from PIL import Image
import numpy as np

app = Flask(__name__)

# Helper functions
def calculate_omega_arag(pco2):
    """
    Calculate the aragonite saturation state (Ωarag) based on atmospheric pCO₂.

    Parameters:
        pco2 (float): Atmospheric pCO₂ in ppm.

    Returns:
        float: Aragonite saturation state (Ωarag).
    """
    omega_arag = max(0, 7.0 - 0.01 * (pco2 - 280))
    return omega_arag

def calculate_health(temperature, pH, pollution, omega_arag):
    """
    Calculate coral reef health based on the given parameters.

    Parameters:
        temperature (float): Water temperature in degrees Celsius.
        pH (float): Water pH level.
        pollution (float): Pollution level (0-100 scale).
        omega_arag (float): Aragonite saturation state.

    Returns:
        float: Coral reef health score (0-100).
    """
    if 23 <= temperature <= 29:
        temp_effect = 100 - 10 * abs(26 - temperature) / 3
    else:
        temp_effect = max(0, 100 - 20 * abs(26 - temperature) / 3)

    if 8.1 <= pH <= 8.3:
        pH_effect = 100 - 50 * abs(8.2 - pH)
    else:
        pH_effect = max(0, 100 - 100 * abs(8.2 - pH))

    pollution_effect = max(0, 100 - pollution * 1.5)

    if omega_arag > 3.5:
        omega_effect = 100
    elif omega_arag > 2.5:
        omega_effect = 75
    elif omega_arag > 1.5:
        omega_effect = 50
    elif omega_arag > 1.0:
        omega_effect = 25
    else:
        omega_effect = 0

    health = (0.3 * temp_effect + 0.3 * pH_effect + 0.2 * pollution_effect + 0.2 * omega_effect)
    return max(0, min(health, 100))

def display_coral_health_image(health):
    """
    Get the path to the image representing the coral reef health.

    Parameters:
        health (float): Coral reef health score (0-100).

    Returns:
        str: Path to the corresponding coral health image.
    """
    if health > 75:
        return "Healthy.png"
    elif health > 50:
        return "stressed.png"
    elif health > 25:
        return "bleached.png"
    else:
        return "dead.png"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            initial_temperature = float(request.form['temperature'])
            initial_pH = float(request.form['pH'])
            initial_pollution = float(request.form['pollution'])
            initial_pco2 = float(request.form['pco2'])

            if not (0 <= initial_pollution <= 100):
                raise ValueError("Pollution level must be between 0 and 100.")

            omega_arag = calculate_omega_arag(initial_pco2)
            health = calculate_health(initial_temperature, initial_pH, initial_pollution, omega_arag)
            coral_image = display_coral_health_image(health)

            # Render the result in the same template or a separate one
            return render_template('index.html', health=health, coral_image=coral_image)
        except ValueError as e:
            return render_template('index.html', error=str(e))

    return render_template('index.html', error=None)

@app.route('/coral-info')
def coral_info():
    return render_template('coral-info.html')


@app.route('/sources')
def sources():
   return render_template('sources.html')



if __name__ == '__main__':
    app.run(debug=True)
