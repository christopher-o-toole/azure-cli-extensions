# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------
# pylint: disable=too-many-lines

from knack.help_files import helps


helps['footprint profile'] = """
    type: group
    short-summary: footprint profile
"""

helps['footprint profile list'] = """
    type: command
    short-summary: Retrieves the information about all Footprint profiles under a subscription.
    examples:
      - name: List all Footprint profiles under a Resource Group.
        text: |-
               az footprint profile list --resource-group "rgName"
"""

helps['footprint profile show'] = """
    type: command
    short-summary: Retrieves the information about a single Footprint profile.
    examples:
      - name: Get the details of a Footprint profile.
        text: |-
               az footprint profile show --name "fpProfile1" --resource-group "rgName"
"""

helps['footprint profile create'] = """
    type: command
    short-summary: Creates or updates a Footprint profile with the specified properties.
    examples:
      - name: Create or update a Footprint profile.
        text: |-
               az footprint profile create --location "westus2" --measurement-count 3 --start-delay-milliseconds 5000 \
--tags key1="value1" key2="value2" --name "fpProfile1" --resource-group "rgName"
"""

helps['footprint profile update'] = """
    type: command
    short-summary: Updates an existing Footprint profile resource.
    examples:
      - name: Update a Footprint profile.
        text: |-
               az footprint profile update --tags key1="value1" key2="value2" --name "fpProfile1" --resource-group \
"rgName"
"""

helps['footprint profile delete'] = """
    type: command
    short-summary: Deletes an existing Footprint profile.
    examples:
      - name: Delete a Footprint profile.
        text: |-
               az footprint profile delete --name "fpProfile1" --resource-group "rgName"
"""

helps['footprint measurement-endpoint'] = """
    type: group
    short-summary: footprint measurement-endpoint
"""

helps['footprint measurement-endpoint list'] = """
    type: command
    short-summary: Retrieves the information about all measurement endpoints under a Footprint profile.
    examples:
      - name: List all the measurement endpoints under a Footprint profile.
        text: |-
               az footprint measurement-endpoint list --profile-name "fpProfile1" --resource-group "rgName"
"""

helps['footprint measurement-endpoint show'] = """
    type: command
    short-summary: Retrieves the information about a single measurement endpoint under a Footprint profile.
    examples:
      - name: Get the details of a measurement endpoint.
        text: |-
               az footprint measurement-endpoint show --name "endpoint1" --profile-name "fpProfile1" --resource-group \
"rgName"
"""

helps['footprint measurement-endpoint create'] = """
    type: command
    short-summary: Creates or updates a single measurement endpoint under a Footprint profile with the specified \
properties.
    examples:
      - name: Create or update a measurement endpoint.
        text: |-
               az footprint measurement-endpoint create --name "endpoint1" --endpoint "www.contoso.com" \
--experiment-id "664cdec4f07d4e1083c9b3969ee2c49b" --measurement-type 2 --object-path "/trans.gif" --weight 10 \
--profile-name "fpProfile1" --resource-group "rgName"
"""

helps['footprint measurement-endpoint update'] = """
    type: command
    short-summary: Creates or updates a single measurement endpoint under a Footprint profile with the specified \
properties.
    examples:
      - name: Create or update a measurement endpoint.
        text: |-
               az footprint measurement-endpoint update --name "endpoint1" --endpoint "www.contoso.com" \
--experiment-id "664cdec4f07d4e1083c9b3969ee2c49b" --measurement-type 2 --object-path "/trans.gif" --weight 10 \
--profile-name "fpProfile1" --resource-group "rgName"
"""

helps['footprint measurement-endpoint delete'] = """
    type: command
    short-summary: Deletes an existing measurement endpoint under a Footprint profile.
    examples:
      - name: Delete a measurement endpoint.
        text: |-
               az footprint measurement-endpoint delete --name "endpoint1" --profile-name "fpProfile1" \
--resource-group "rgName"
"""

helps['footprint measurement-endpoint-condition'] = """
    type: group
    short-summary: footprint measurement-endpoint-condition
"""

helps['footprint measurement-endpoint-condition list'] = """
    type: command
    short-summary: Retrieves the information about all measurement endpoint conditions under a Footprint measurement \
endpoint.
    examples:
      - name: List all conditions under a measurement endpoint.
        text: |-
               az footprint measurement-endpoint-condition list --measurement-endpoint-name "endpoint1" --profile-name \
"fpProfile1" --resource-group "rgName"
"""

helps['footprint measurement-endpoint-condition show'] = """
    type: command
    short-summary: Retrieves the information about a single measurement endpoint condition under a Footprint \
measurement endpoint.
    examples:
      - name: Get the details of a measurement endpoint condition.
        text: |-
               az footprint measurement-endpoint-condition show --condition-name "condition0" \
--measurement-endpoint-name "endpoint1" --profile-name "fpProfile1" --resource-group "rgName"
"""

helps['footprint measurement-endpoint-condition create'] = """
    type: command
    short-summary: Creates or updates a measurement endpoint condition under a Footprint measurement with the \
specified properties.
    examples:
      - name: Create or update a measurement endpoint condition.
        text: |-
               az footprint measurement-endpoint-condition create --condition-name "condition0" \
--measurement-endpoint-name "endpoint1" --constant "Edge-Prod-WST" --operator "MatchValueIgnoreCasing" --variable \
"X-FD-EdgeEnvironment" --profile-name "fpProfile1" --resource-group "rgName"
"""

helps['footprint measurement-endpoint-condition update'] = """
    type: command
    short-summary: Creates or updates a measurement endpoint condition under a Footprint measurement with the \
specified properties.
    examples:
      - name: Create or update a measurement endpoint condition.
        text: |-
               az footprint measurement-endpoint-condition update --condition-name "condition0" \
--measurement-endpoint-name "endpoint1" --constant "Edge-Prod-WST" --operator "MatchValueIgnoreCasing" --variable \
"X-FD-EdgeEnvironment" --profile-name "fpProfile1" --resource-group "rgName"
"""

helps['footprint measurement-endpoint-condition delete'] = """
    type: command
    short-summary: Deletes an existing measurement endpoint condition under a Footprint measurement.
    examples:
      - name: Delete a measurement endpoint condition.
        text: |-
               az footprint measurement-endpoint-condition delete --condition-name "condition0" \
--measurement-endpoint-name "endpoint1" --profile-name "fpProfile1" --resource-group "rgName"
"""

helps['footprint experiment'] = """
    type: group
    short-summary: footprint experiment
"""

helps['footprint experiment list'] = """
    type: command
    short-summary: Retrieves the information about all experiments under a Footprint profile.
    examples:
      - name: List all experiments under a Footprint profile.
        text: |-
               az footprint experiment list --profile-name "fpProfile1" --resource-group "rgName"
"""

helps['footprint experiment show'] = """
    type: command
    short-summary: Retrieves the information about a single Footprint experiment.
    examples:
      - name: Get the details of an experiment.
        text: |-
               az footprint experiment show --name "fpExp1" --profile-name "fpProfile1" --resource-group "rgName"
"""

helps['footprint experiment create'] = """
    type: command
    short-summary: Creates or updates a Footprint experiment with the specified properties.
    examples:
      - name: Create or update an experiment.
        text: |-
               az footprint experiment create --name "fpExp1" --description "An experiment description." \
--profile-name "fpProfile1" --resource-group "rgName"
"""

helps['footprint experiment update'] = """
    type: command
    short-summary: Creates or updates a Footprint experiment with the specified properties.
    examples:
      - name: Create or update an experiment.
        text: |-
               az footprint experiment update --name "fpExp1" --description "An experiment description." \
--profile-name "fpProfile1" --resource-group "rgName"
"""

helps['footprint experiment delete'] = """
    type: command
    short-summary: Deletes an existing Footprint experiment.
    examples:
      - name: Delete an experiment.
        text: |-
               az footprint experiment delete --name "fpExp1" --profile-name "fpProfile1" --resource-group "rgName"
"""
