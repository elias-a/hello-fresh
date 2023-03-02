# HelloFresh Meal Predictor

A program that predicts which HelloFresh meals you'll enjoy based on your previous selections.

## Requirements

* Python 3.11 or later
* HelloFresh account
* Google Chrome installation

## Overview

The HelloFresh Meal Predictor connects to a HelloFresh account and observes the meals that have been delivered in past weeks. Based on these previous selections, the program predicts the meals that you'll most enjoy for an upcoming week. By setting a more personalized baseline for your HelloFresh meals, the Meal Predictor saves a bit of time by reducing the need to remove the default meals that you may find unsavory.

## Setup

To use the Meal Predictor program, clone this repository and run

```
pip install -r requirements.txt
```

Create a file called `config.ini` with the following format:

```
[HELLO_FRESH]
email = <hellofresh_email>
password = <hellofresh_password>
subscriptionId = <hellofresh_subscription_id>
```

To execute the program and update your selected HelloFresh meals for the upcoming week, run

```
python main.py --action=all
```

A log file named `hello-fresh.log` will be saved to the root directory of the project and contain details of the program's execution.
