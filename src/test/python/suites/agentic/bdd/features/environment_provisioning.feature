Feature: Environment Provisioning
  As a developer
  I want to provision and release test environments via the API
  So that I can run tests in isolated namespaces

  Scenario: List existing reservations
    Given the agent API is accessible
    When I request the list of reservations
    Then the response status is 200
    And the response is a list

  Scenario: Create a K8s environment reservation
    Given the agent API is accessible
    When I create a K8s reservation with TTL 30 minutes
    Then the response status is 200 or 201 or 409
    And the reservation has an ID if created

  Scenario: Invalid role is rejected
    Given the agent API is accessible
    When I request reservations with role "superadmin"
    Then the response status is 400
    And the response contains "detail"
