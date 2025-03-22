# Systems Analysis Schema Validation Documentation for EBR-II

## Table of Contents

1.  [Introduction](#introduction)
2.  [Schema Overview](#schema-overview)
3.  [Regulatory Requirements Coverage](#Regulatory-requirements-coverage)
    1.  [SY-C1: Process Documentation](#sy-c1-process-documentation)
        1.  [(a) System Function and Operation](#a-system-function-and-operation)
        2.  [(b) System Model Boundary](#b-system-model-boundary)
        3.  [(c) System Schematic](#c-system-schematic)
        4.  [(d) Equipment Operability](#d-equipment-operability)
        5.  [(e) Operational History](#e-operational-history)
        6.  [(f) Success Criteria](#f-success-criteria)
        7.  [(g) Human Actions](#g-human-actions)
        8.  [(h) Test and Maintenance](#h-test-and-maintenance)
        9.  [(i) System Dependencies](#i-system-dependencies)
        10. [(j) Component Spatial Information](#j-component-spatial-information)
        11. [(k) Modeling Assumptions](#k-modeling-assumptions)
        12. [(l) Components and Failure Modes](#l-components-and-failure-modes)
        13. [(m) Modularization Process](#m-modularization-process)
        14. [(n) Logic Loop Resolution](#n-logic-loop-resolution)
        15. [(o) Evaluation Results](#o-evaluation-results)
        16. [(p) Sensitivity Studies](#p-sensitivity-studies)
        17. [(q) Information Sources](#q-information-sources)
        18. [(r) Basic Events Traceability](#r-basic-events-traceability)
        19. [(s) Nomenclature](#s-nomenclature)
        20. [(t) Digital I&C Systems](#t-digital-ic-systems)
        21. [(u) Passive Systems](#u-passive-systems)
    2.  [SY-C2: Model Uncertainty Documentation](#sy-c2-model-uncertainty-documentation)
    3.  [SY-C3: Pre-Operational Assumptions Documentation](#sy-c3-pre-operational-assumptions-documentation)
4.  [Implementation Examples](#implementation-examples)
    1.  [EBR-II Passive Safety Features Example](#ebr-ii-passive-safety-features-example)
    2.  [EBR-II Shutdown Cooling System Example](#ebr-ii-shutdown-cooling-system-example)
5.  [Requirements Coverage Summary](#requirements-coverage-summary)
6.  [Conclusion](#conclusion)

## Introduction

This document validates that the TypeScript schema for Systems Analysis is ideally suited for the comprehensive documentation of the **Experimental Breeder Reactor-II (EBR-II)**. Leveraging the "Supporting Requirements" as defined in a standard, this schema provides structured interfaces and data structures that enable a thorough and traceable analysis of EBR-II's systems.

The primary objective of Regulatory guidance is to ensure that the documentation of Systems Analysis provides **traceability of the work**. The TypeScript schema implements this through structured interfaces that capture all required information specific to EBR-II's unique design and operational history.

## Schema Overview

The Systems Analysis TypeScript schema implements a comprehensive set of interfaces and types that enable detailed documentation of EBR-II's system models, dependencies, uncertainties, and assumptions as required for a Probabilistic Risk Assessment (PRA). Key modules within the schema are directly applicable to EBR-II:

*   **Core definitions and enumerations**: Provides foundational data types relevant to nuclear power plant components and states.
*   **System modeling and failure modes**: Allows for structured representation of EBR-II's front-line and support systems, including their potential failure modes. This is crucial for capturing the unique aspects of a liquid metal fast breeder reactor.
*   **Fault tree analysis**: Facilitates the development and quantification of fault trees for EBR-II systems, as was done in the Level 1 PRA.
*   **Dependencies and common cause analysis**: Enables the explicit modelling of dependencies between EBR-II systems, a key focus of the PRA due to the limited active mitigative functions. It also supports the treatment of common cause failures.
*   **Engineering analysis and validation**: Allows for linking system models to supporting engineering analyses, such as the **SASSYS code** used for thermal-hydraulic analyses of EBR-II transients.
*   **Documentation and traceability**: Provides a structured framework to ensure all aspects of the Systems Analysis for EBR-II are well-documented and traceable to underlying data and assumptions.

The schema provides dedicated interfaces for meeting Regulatory requirements, including `ProcessDocumentation`, `ModelUncertaintyDocumentation`, and other interfaces that inherit from base documentation classes.

Additionally, the schema includes minimal interfaces for specific system aspects directly relevant to EBR-II:

*   `SupportSystemSuccessCriteria`: Essential for defining the success criteria of EBR-II's support systems, such as the cooling water systems and electrical systems.
*   `EnvironmentalDesignBasisConsideration`: Important for considering the operating environment of EBR-II components, including the presence of liquid sodium.
*   `InitiationActuationSystem`: Applicable to modelling EBR-II's Reactor Shutdown System (RSS) and its actuation logic.

The schema provides dedicated interfaces for meeting Regulatory requirements, including `ProcessDocumentation`, `ModelUncertaintyDocumentation`, and other interfaces that inherit from base documentation classes.

## Regulatory Requirements Coverage

This section demonstrates how the schema enables comprehensive compliance with each of the supporting requirements for Regulatory Compliance in the context of the EBR-II reactor.

### SY-C1: Process Documentation

The schema provides the `ProcessDocumentation` interface that extends `BaseProcessDocumentation` with systems-specific documentation requirements, perfectly aligning with the detailed systems analyses performed for the EBR-II Level 1 PRA.

```typescript
export interface ProcessDocumentation extends BaseProcessDocumentation {
  systemFunctionDocumentation?: Record<string, string>;
  systemBoundaryDocumentation?: Record<string, string[]>;
  systemSchematicReferences?: Record<string, { reference: string; description?: string }>;
  equipmentOperabilityDocumentation?: Record<string, { system: SystemReference; component: string; considerations: string; calculationReferences?: string[] }>;
  // Additional properties addressing SY-C1 requirements
  // ...
}
```

The following sections demonstrate how each SY-C1 sub-requirement is covered by the schema with concise examples specifically for EBR-II.

#### (a) System Function and Operation

**Schema Coverage:**

```typescript
// ProcessDocumentation interface
systemFunctionDocumentation?: Record<string, string>;
// Also in SystemDefinition interface
description?: string;
```

**Example (EBR-II Reactor Shutdown System - RSS):**

```typescript
const processDoc: ProcessDocumentation = {
  systemFunctionDocumentation: {
    "SYS-RSS": "The EBR-II Reactor Shutdown System is designed to automatically shut down the reactor (scram) by inserting control and safety rods in the event of off-normal conditions to prevent fuel damage, personnel injury, or release of contamination."
  }
};
```

#### (b) System Model Boundary

**Schema Coverage:**

```typescript
// ProcessDocumentation interface
systemBoundaryDocumentation?: Record<string, string[]>;
// Also in SystemDefinition interface
boundaries: string[];
```

**Example (EBR-II Primary Sodium System):**

```typescript
const systemDef: SystemDefinition = {
  id: "SYS-PrimarySodium",
  name: "Primary Sodium System",
  boundaries: [
    "Reactor vessel inlet plenum",
    "Reactor core and blanket assemblies",
    "Reactor vessel outlet plenum",
    "Primary sodium pumps (including motor/generator sets)",
    "Intermediate Heat Exchanger (IHX)",
    "All associated primary sodium piping submerged within the primary tank"
  ]
};
```

#### (c) System Schematic

**Schema Coverage:**

```typescript
// ProcessDocumentation interface
systemSchematicReferences?: Record<string, { reference: string; description?: string }>;
// Also in SystemDefinition interface
schematic?: {
  reference: string;
  description?: string;
};
```

**Example (EBR-II Primary System):**

```typescript
const processDoc: ProcessDocumentation = {
  systemSchematicReferences: {
    "SYS-PrimarySodium": {
      reference: "Figure 2-11, Experimental Breeder Reactor by Leonard Koch.pdf",
      description: "EBR-II Primary Piping and Component Arrangement."
    },
    "SYS-ShutdownCooling": {
      reference: "Figure 2-13, Experimental Breeder Reactor by Leonard Koch.pdf",
      description: "EBR-II Shutdown Cooling System schematic."
    }
  }
};
```

#### (d) Equipment Operability

**Schema Coverage:**

```typescript
// ProcessDocumentation interface
equipmentOperabilityDocumentation?: Record<string, { system: SystemReference; component: string; considerations: string; calculationReferences?: string[] }>;
// Also in SystemDefinition interface
operabilityConsiderations?: {
  component: string;
  calculationRef?: string;
  notes?: string;
}[];
```

**Example (EBR-II Primary Pump):**

```typescript
const systemDef: SystemDefinition = {
  // Other properties...
  operabilityConsiderations: [
    {
      component: "Primary Sodium Pump P-1",
      calculationRef: null, // Referencing EBR-II operational experience
      notes: "EBR-II primary pumps have demonstrated reliable operation within the specified temperature and flow ranges over a long operating history."
    }
  ]
};
```

#### (e) Operational History

**Schema Coverage:**

```typescript
// ProcessDocumentation interface
operationalHistoryDocumentation?: Record<string, string[]>;
// Also in SystemDefinition interface
operationalHistory?: string[];
```

**Example (EBR-II Shutdown Cooling System):**

```typescript
const processDoc: ProcessDocumentation = {
  operationalHistoryDocumentation: {
    "SYS-ShutdownCooling": [
      "The passive shutdown cooling system has been analyzed extensively and its behavior confirmed by experiments performed in EBR-II.",
      "Natural circulation capability is a key feature of EBR-II, designed for reliable decay heat removal independent of external power."
    ]
  }
};
```

#### (f) Success Criteria

**Schema Coverage:**

```typescript
// ProcessDocumentation interface
successCriteriaDocumentation?: Record<string, { criteria: string; relationshipToEventSequences: string }>;
// Also in SystemDefinition interface
successCriteria: string | SystemSuccessCriterion | SuccessCriteriaId;
// Also in SupportSystemSuccessCriteria interface
export interface SupportSystemSuccessCriteria extends Unique {
  systemReference: SystemReference;
  successCriteria: string;
  criteriaType: "conservative" | "realistic";
  supportedSystems: SystemReference[];
}
```

**Example (EBR-II Reactor Shutdown System Success Criteria):**

```typescript
const processDoc: ProcessDocumentation = {
  successCriteriaDocumentation: {
    "SYS-RSS": {
      criteria: "Insertion of a sufficient number of control and/or safety rods to achieve and maintain reactor subcriticality following a transient.",
      relationshipToEventSequences: "Critical for mitigating the consequences of all reactivity insertion events and general transients."
    }
  }
};

// Example for support system success criteria (EBR-II Shield Cooling System)
const supportSystemCriteria: SupportSystemSuccessCriteria = {
  id: "SSSC-ShieldCooling-001",
  systemReference: "SYS-ShieldCooling",
  successCriteria: "Maintain adequate cooling to prevent overheating of reactor shielding components.",
  criteriaType: "realistic",
  supportedSystems: ["SYS-ReactorVessel"]
};
```

#### (g) Human Actions

**Schema Coverage:**

```typescript
// ProcessDocumentation interface
humanActionsDocumentation?: Record<string, { system: SystemReference; description: string }>;
// Also in SystemDefinition interface
humanActionsForOperation?: {
  actionRef: HumanActionReference;
  description: string;
}[];
```

**Example (EBR-II Manual Scram):**

```typescript
const systemDef: SystemDefinition = {
  // Other properties...
  humanActionsForOperation: [
    {
      actionRef: "HRA-ManualScram-001",
      description: "Operator manually initiates a reactor scram upon recognition of an off-normal condition that does not automatically trigger the RSS."
    }
  ]
};
```

#### (h) Test and Maintenance

**Schema Coverage:**

```typescript
// ProcessDocumentation interface
testMaintenanceProceduresDocumentation?: Record<string, string[]>;
// Also in SystemDefinition interface
testMaintenanceProcedures?: string[];
testAndMaintenance?: string[];
```

**Example (EBR-II Reactor Shutdown System Testing):**

```typescript
const processDoc: ProcessDocumentation = {
  testMaintenanceProceduresDocumentation: {
    "SYS-RSS": [
      "Periodic testing of control and safety rod scram times and operability is performed with the reactor shutdown before returning to power."
    ]
  }
};
```

#### (i) System Dependencies

**Schema Coverage:**

```typescript
// ProcessDocumentation interface
dependencySearchDocumentation?: {
  methodology: string;
  dependencyTableReferences: string[];
};
// Also in dedicated interfaces
export interface SystemDependency extends Unique {
  dependentSystem: SystemReference;
  supportingSystem: SystemReference;
  type: DependencyType | string;
  // Other properties...
}
export interface DependencySearchMethodology extends Unique, Named {
  description: string;
  // ...
}
```

**Example (EBR-II Shutdown Cooling System Dependency):**

```typescript
const processDoc: ProcessDocumentation = {
  dependencySearchDocumentation: {
    methodology: "Dependencies identified through system walkdowns with cognizant EBR-II engineers and review of system documentation."
    dependencyTableReferences: ["Table 6.1, 1_EBR2_PRA_ANL.pdf"]
  }
};

const systemDependency: SystemDependency = {
  id: "Dep-SCS-AirCooling",
  dependentSystem: "SYS-ShutdownCooling",
  supportingSystem: "SYS-StackExhaust", // For air cooling of the NaK loop
  type: "Functional"
};
```

#### (j) Component Spatial Information

**Schema Coverage:**

```typescript
// ProcessDocumentation interface
spatialInformationDocumentation?: Record<string, { location: string; systems: SystemReference[]; components: string[]; hazards: string[] }>;
// Also in SystemDefinition interface
spatialInformation?: {
  location: string;
  hazards?: string[];
  components?: string[];
}[];
```

**Example (EBR-II Primary Tank):**

```typescript
const systemDef: SystemDefinition = {
  // Other properties...
  spatialInformation: [
    {
      location: "EBR-II Primary Tank",
      hazards: ["High radiation levels", "Liquid sodium at elevated temperature"],
      components: ["Reactor core", "Primary sodium pumps", "Intermediate Heat Exchanger", "Fuel Handling System"]
    }
  ]
};
```

#### (k) Modeling Assumptions

**Schema Coverage:**

```typescript
// ProcessDocumentation interface
modelingAssumptionsDocumentation?: Record<string, string[]>;
// Also in SystemDefinition interface
modelAssumptions?: string[];
```

**Example (EBR-II Passive Safety Modeling):**

```typescript
const processDoc: ProcessDocumentation = {
  modelingAssumptionsDocumentation: {
    "EBR-II Core": [
      "The negative temperature coefficient of reactivity provides inherent feedback to reduce power during over-temperature conditions."
      "Natural circulation of primary sodium is established and sufficient for decay heat removal upon loss of forced flow."
    ]
  }
};
```

#### (l) Components and Failure Modes

**Schema Coverage:**

```typescript
// ProcessDocumentation interface
componentsFailureModesDocumentation?: Record<string, { includedComponents: string[]; excludedComponents: string[]; justificationForExclusion: string; includedFailureModes: string[]; excludedFailureModes: string[]; justificationForFailureModeExclusion: string }>;
// Also in SystemDefinition interface
modeledComponentsAndFailures: Record<string, { failureModes: string[]; justificationForInclusion?: string; componentGroup?: string }>;
justificationForExclusionOfComponents?: string[];
justificationForExclusionOfFailureModes?: string[];
```

**Example (EBR-II Primary Pump Failure Modes):**

```typescript
const systemDef: SystemDefinition = {
  // Other properties...
  modeledComponentsAndFailures: {
    "PrimaryPump-01": {
      failureModes: ["Failure to start", "Failure to run", "Loss of flow"],
      justificationForInclusion: "Essential component for forced circulation of primary coolant."
    },
    "ControlRod-01": {
      failureModes: ["Failure to insert", "Failure to withdraw"],
      justificationForInclusion: "Key component of the Reactor Shutdown System."
    }
  },
  justificationForExclusionOfComponents: [
    "Small bore instrumentation valves excluded due to negligible impact on system-level failure."
  ]
};
```

#### (m) Modularization Process

**Schema Coverage:**

```typescript
// ProcessDocumentation interface
modularizationDocumentation?: {
  description: string;
  systems: SystemReference[];
};
```

**Example (EBR-II PRA Modularization):**

```typescript
const processDoc: ProcessDocumentation = {
  modularizationDocumentation: {
    description: "The EBR-II Level 1 PRA adopted a 'small event tree-linked fault tree' approach, where accident sequences are defined using concise event trees, and system failures are modeled with detailed fault trees."
    systems: ["SYS-RSS", "SYS-PrimaryPumps", "SYS-ShutdownCooling"]
  }
};
```

#### (n) Logic Loop Resolution

**Schema Coverage:**

```typescript
// ProcessDocumentation interface
logicLoopResolutionsDocumentation?: Record<string, { system: SystemReference; loopDescription: string; resolution: string }>;
// Also in SystemLogicModel interface
logicLoopResolutions?: {
  loopId: string;
  resolution: string;
}[];
```

**Example (EBR-II Electrical Power Dependency):**

```typescript
const sysLogicModel: SystemLogicModel = {
  id: "SLM-ShutdownCooling-001",
  systemReference: "SYS-ShutdownCooling",
  description: "Fault Tree for the EBR-II Shutdown Cooling System",
  modelRepresentation: "See Appendix C of 1_EBR2_PRA_ANL.pdf",
  basicEvents: [],
  logicLoopResolutions: [
    {
      loopId: "Loop-SCS-ElectricalDependency",
      resolution: "While EBR-II has little electrical power requirement to prevent fuel damage, support systems like the Stack Exhaust System (for air cooling) rely on electrical power. This dependency was addressed by modelling power availability in the fault trees of the supporting systems."
    }
  ]
};
```

#### (o) Evaluation Results

**Schema Coverage:**

```typescript
// ProcessDocumentation interface
evaluationResultsDocumentation?: Record<string, { topEventProbability: number; otherResults: Record<string, any> }>;
// Also in SystemModelEvaluation interface
export interface SystemModelEvaluation extends Unique {
  system: SystemReference;
  topEventProbability?: number;
  quantitativeResults?: Record<string, any>;
  qualitativeInsights?: string[];
  dominantContributors?: { contributor: string; contribution: number }[];
}
```

**Example (EBR-II Core Damage Frequency Comparison):**

```typescript
const processDoc: ProcessDocumentation = {
  evaluationResultsDocumentation: {
    topEventProbability: null, // Overall core damage frequency reported in the full PRA report
    otherResults: {
      "Core Damage Frequency Comparison": "The EBR-II PRA results were compared to those for commercial LWRs (NUREG-1150) and other USDOE facilities to assess the relative level of risk."
    }
  }
};
```

#### (p) Sensitivity Studies

**Schema Coverage:**

```typescript
// ProcessDocumentation interface
sensitivityStudiesDocumentation?: Record<string, { studyDescription: string; results: string }>;
// Also in dedicated interface
export interface SystemSensitivityStudy extends SensitivityStudy {
  system: SystemReference;
  parameterChanged: string;
  impactOnSystem: string;
  insights?: string;
}
```

**Example (EBR-II Reactivity Feedback Sensitivity):**

```typescript
const sensitivityStudy: SystemSensitivityStudy = {
  id: "Sens-Core-ReactivityFeedback",
  name: "Sensitivity of Core Damage Frequency to Reactivity Feedback Coefficients",
  system: "SYS-Core",
  parameterChanged: "Magnitude of the negative temperature coefficient of reactivity",
  impactOnSystem: "Variations in the reactivity feedback coefficients can influence the severity and outcome of transient events.",
  insights: "Analysis of EBR-II transients using the SASSYS code incorporated best estimate feedback characteristics."
};
```

#### (q) Information Sources

**Schema Coverage:**

```typescript
// ProcessDocumentation interface
informationSourcesDocumentation?: {
  drawings: string[];
  procedures: string[];
  interviews: string[];
  otherSources: string[];
};
```

**Example (EBR-II PRA Information Sources):**

```typescript
const processDoc: ProcessDocumentation = {
  informationSourcesDocumentation: {
    drawings: ["EBR-II System Design Descriptions (SDDs)", "Piping and Instrumentation Diagrams (P&IDs)"],
    procedures: ["Operating Instructions", "Maintenance Procedures"],
    interviews: ["Interactions with EBR-II management and operating personnel"],
    otherSources: ["EBR-II Hazard Summary Report (ANL-5719)", "EBR-II Technical Specifications", "Generic PRA Literature", "LMR Plant Data", "EBR-II Plant-Specific Data"]
  }
};
```

#### (r) Basic Events Traceability

**Schema Coverage:**

```typescript
// ProcessDocumentation interface
basicEventsDocumentation?: Record<string, { system: SystemReference; description: string; moduleReference?: string; cutsetReference?: string }>;
// Also in FaultTree interface
export interface FaultTree extends Unique, Named {
  systemReference: SystemReference;
  nodes: Record<string, FaultTreeNode>;
  minimalCutSets?: string[][];
  // Other properties...
}
```

**Example (EBR-II Fault Tree Basic Event):**

```typescript
const processDoc: ProcessDocumentation = {
  basicEventsDocumentation: {
    "BE-Pump01-FailToStart": {
      system: "SYS-PrimaryPumps",
      description: "Primary Sodium Pump P-1 fails to start on demand",
      moduleReference: "MOD-PrimaryPump",
      cutsetReference: "CutSet-LOF-001"
    }
  }
};
```

#### (s) Nomenclature

**Schema Coverage:**

```typescript
// ProcessDocumentation interface
nomenclatureDocumentation?: Record<string, string>;
// Also in SystemLogicModel interface
nomenclature?: Record<string, string>;
```

**Example (EBR-II System Nomenclature):**

```typescript
const sysLogicModel: SystemLogicModel = {
  // Other properties...
  nomenclature: {
    "RSS": "Reactor Shutdown System",
    "IHX": "Intermediate Heat Exchanger",
    "LOF": "Loss of Flow",
    "LOCA": "Loss-of-Coolant-Accident (analogous to Loss-of-Sodium Accident in EBR-II)"
  }
};
```

#### (t) Digital I&C Systems

**Schema Coverage:**

```typescript
// ProcessDocumentation interface
digitalICDocumentation?: Record<string, { description: string; modelingApproach: string; specialConsiderations?: string }>;
// Also in dedicated interface
export interface DigitalInstrumentationAndControl extends Unique, Named {
  systemReference: SystemReference;
  description: string;
  methodology: string;
  assumptions?: string[];
  failureModes?: string[];
  specialConsiderations?: string[];
}
```

**Example (EBR-II Instrumentation - Predominantly Analogue):**

```typescript
const processDoc: ProcessDocumentation = {
  digitalICDocumentation: {
    "EBR-II Instrumentation": {
      description: "EBR-II utilized primarily analogue instrumentation and control systems. The PRA modelling accounted for potential failures of these components using standard reliability data and fault tree analysis.",
      modelingApproach: "Traditional fault tree modelling of analogue components.",
      specialConsiderations: "Ageing effects and plant-specific data were considered where available."
    }
  }
};
```

#### (u) Passive Systems

**Schema Coverage:**

```typescript
// ProcessDocumentation interface
passiveSystemsDocumentation?: Record<string, { description: string; uncertaintyEvaluation: string }>;
// Also in dedicated interface
export interface PassiveSystemsTreatment extends Unique, Named {
  systemReference: SystemReference;
  description: string;
  performanceAnalysisRef?: string;
  uncertaintyAnalysis?: string;
  relevantPhysicalPhenomena?: string[];
  uncertaintyEvaluation?: string;
}
```

**Example (EBR-II Passive Safety Features):**

```typescript
const passiveSys: PassiveSystemsTreatment = {
  id: "PST-EBRII-PassiveSafety",
  name: "EBR-II Inherent Safety Characteristics",
  systemReference: "SYS-Reactor",
  description: "**EBR-II possesses unique passive safety features** that enhance its ability to withstand accident sequences without core damage relying on natural phenomena rather than active components.",
  relevantPhysicalPhenomena: ["Negative temperature coefficient of reactivity", "Natural convection decay heat removal"],
  uncertaintyEvaluation: "The effectiveness of EBR-II's passive safety features has been extensively analyzed using the SASSYS code, with consideration of uncertainties in reactivity feedbacks and thermal-hydraulic parameters."
};
```

### SY-C2: Model Uncertainty Documentation

The schema includes the `ModelUncertaintyDocumentation` interface that extends `BaseModelUncertaintyDocumentation` to explicitly address SY-C2 requirements for EBR-II.

```typescript
export interface ModelUncertaintyDocumentation extends BaseModelUncertaintyDocumentation {
  systemSpecificUncertainties?: Record<string, { uncertainties: string[]; impact: string }>;
  reasonableAlternatives: {
    alternative: string;
    reasonNotSelected: string;
    applicableSystems?: SystemReference[];
  }[];
}
```

This interface allows for documenting sources of model uncertainty specific to EBR-II, related assumptions (as covered in SY-C1(k)), and reasonable alternative modeling approaches that might have been considered during the PRA. For example, uncertainties in component failure rates derived from generic data versus EBR-II specific data, or the impact of different thermal-hydraulic models on accident progression analysis using SASSYS. The consideration of completeness uncertainty due to the uniqueness of EBR-II can also be captured here.

### SY-C3: Pre-Operational Assumptions Documentation

The schema leverages the base `PreOperationalAssumption` interface type which is imported from the core documentation module. While EBR-II is an operational reactor, this section can be adapted to document key assumptions made at the initiation of the PRA in 1989, such as the plant configuration as of a specific date, and the availability of specific operating procedures. This ensures clarity on the baseline conditions considered in the analysis.

## Implementation Examples

This section provides more detailed examples of how the schema enables thorough documentation of key EBR-II systems.

### EBR-II Passive Safety Features Example

```typescript
const passiveSafetyFeatures: PassiveSystemsTreatment = {
  id: "PSF-EBR-II-001",
  name: "EBR-II Passive Reactivity Feedback",
  systemReference: "SYS-CORE",
  description: "**The EBR-II core design incorporates a strong negative temperature coefficient of reactivity.** This inherent characteristic causes a decrease in reactor power as the core temperature increases, providing a natural mechanism to limit power excursions without the need for active control system intervention.",
  relevantPhysicalPhenomena: [
    "Negative temperature coefficient of reactivity arising from fuel expansion, Doppler broadening, and structural expansion."
  ],
  uncertaintyAnalysis: "Uncertainties in the reactivity feedback coefficients were addressed through a review of reactor physics calculations and operational data analysis.",
  uncertaintyEvaluation: "**The SASSYS code simulations of unprotected transients (e.g., unprotected loss of flow - ULOF) demonstrated the effectiveness of this negative feedback in preventing core damage.**"
};

const processDocumentation: ProcessDocumentation = {
  // Other documentation properties...
  passiveSystemsDocumentation: {
    "SYS-CORE": {
      description: "**EBR-II's inherent safety is significantly enhanced by its passive reactivity feedback mechanisms.** These features were a key consideration in the PRA, demonstrating a reduced reliance on active safety systems.",
      uncertaintyEvaluation: "The range of uncertainty in the reactivity coefficients was considered in the bounding analyses of key accident scenarios."
    }
  }
};
```

### EBR-II Shutdown Cooling System Example

```typescript
const shutdownCoolingSystem: SystemDefinition = {
  id: "SYS-SCS-001",
  name: "EBR-II Shutdown Cooling System",
  description: "**The EBR-II Shutdown Cooling System (SCS) is a passive system designed to remove decay heat from the primary sodium following reactor shutdown, particularly when the secondary heat removal system is unavailable.** The system relies on natural convection of both the primary sodium and a secondary sodium-potassium (NaK) loop, ultimately rejecting heat to the atmosphere via air-cooled heat exchangers.",
  boundaries: [
    "Interface with the primary tank bulk sodium.",
    "Natural circulation loop containing NaK eutectic.",
    "Immersion-type bayonet heat exchangers in the primary tank.",
    "Air-cooled heat exchangers (shutdown coolers) located in the stack exhaust system."
  ],
  successCriteria: "**Maintain the bulk primary sodium temperature below a specified limit to prevent fuel or structural damage during shutdown conditions solely through natural convection.**",
  modelAssumptions: [
    "Natural convection flow rates in the primary and secondary (NaK) loops are sufficient to remove decay heat loads.",
    "Air flow through the shutdown coolers is maintained (possibly passively via natural draft or assisted by the stack exhaust fans).",
    "The bayonet heat exchangers provide adequate heat transfer between the primary sodium and the NaK loop."
  ]
};
```

## Requirements Coverage Summary

The following table provides a condensed summary of how the schema enables comprehensive compliance with Regulatory requirements for EBR-II:

| Requirement | Schema Implementation | EBR-II Compliance |
| :---------- | :-------------------- | :---------------- |
| **SY-C1**   | `ProcessDocumentation` interface with 21 specialised properties | ✅ **Complete and directly applicable to documenting the extensive systems analysis performed for the EBR-II PRA.** |
| **SY-C2**   | `ModelUncertaintyDocumentation` interface | ✅ **Complete and allows for detailed recording of uncertainties inherent in modelling a unique reactor like EBR-II.** |
| **SY-C3**   | Base documentation imports including `PreOperationalAssumption` | ✅ **Adaptable for documenting key baseline assumptions at the time of PRA initiation.** |
| **SY-B7/B8** | `SupportSystemSuccessCriteria` interface | ✅ **Essential for defining success criteria for EBR-II's support systems.** |
| **SY-B11/B12**| `InitiationActuationSystem` interface | ✅ **Applicable to modelling the EBR-II Reactor Shutdown System.** |
| **SY-B14**  | `EnvironmentalDesignBasisConsideration` interface | ✅ **Important for considering the unique environment of liquid sodium and potential hazards.** |

### SY-C1 Documentation Structure

The schema's `ProcessDocumentation` interface comprehensively addresses all 21 sub-requirements of SY-C1 for EBR-II through a systematic property mapping:

| Documentation Category | SY-C1 Requirements | Interface Properties                                                                                                                                                                                                                                                                                                                                                                                          | EBR-II Application                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| :--------------------- | :------------------ | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| System Definition      | (a)(b)(c)(f)         | `systemFunctionDocumentation`, `systemBoundaryDocumentation`, `systemSchematicReferences`, `successCriteriaDocumentation`                                                                                                                                                                                                                                                                                                  | **Allows for detailed description of EBR-II system functions (e.g., RSS, primary cooling), clear definition of system boundaries (e.g., primary tank), referencing EBR-II