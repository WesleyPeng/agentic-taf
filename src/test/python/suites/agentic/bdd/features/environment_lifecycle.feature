Feature: Environment Lifecycle and Rollback
  As a platform operator
  I want environments to follow proper lifecycle transitions
  So that failed or expired environments are cleaned up reliably

  Scenario: Release an active reservation
    Given the agent API is accessible
    When I create a K8s reservation with TTL 30 minutes
    And the reservation has an ID if created
    And I release the reservation
    Then the release response status is 200 or 204 or 409

  Scenario: Release a non-existent reservation
    Given the agent API is accessible
    When I release a reservation with ID "non-existent-id-12345"
    Then the release response status is 404 or 409

  Scenario: Get reservation details
    Given the agent API is accessible
    When I create a K8s reservation with TTL 30 minutes
    And the reservation has an ID if created
    And I get the reservation details
    Then the response status is 200
    And the reservation state is valid
    And I release the reservation
