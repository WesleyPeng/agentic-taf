Feature: LLM Routing
  As a platform operator
  I want the agent to use multiple LLM tiers
  So that it can fall back gracefully when a tier is unavailable

  Scenario: Three LLM tiers are configured
    Given the agent API is accessible
    When I check the health endpoint
    Then the health status is "ok"
    And there are 3 LLM routing tiers

  Scenario: All LLM tiers have required fields
    Given the agent API is accessible
    When I check the LLM models endpoint
    Then each model has tier, name, and label fields
