import gherkan.utils.gherkin_keywords as g

sectionDict = {  # Dictionary of the possible sectioning denominators; add any synonymes and translations to each list
    g.FEATURE: [g.FEATURE, g.FEATURE_CS],
    g.BACKGROUND: [g.BACKGROUND, g.BACKGROUND_CS],
    g.SCENARIO: [g.SCENARIO, g.SCENARIO_CS],
    g.GIVEN: [g.GIVEN, g.GIVEN_CS],
    g.WHEN: [g.WHEN, g.WHEN_CS],
    g.THEN: [g.THEN, g.THEN_CS],
    g.AND: [g.AND, g.AND_CS],
}
