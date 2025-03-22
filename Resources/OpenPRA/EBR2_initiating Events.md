### 5.2 Sample Implementation for EBR-II

Below is a sample partial implementation of the schema for EBR-II initiating event analysis, demonstrating how the schema satisfies the documentation requirements for a specific sodium-cooled fast reactor:

```typescript
const ebrIIAnalysis: InitiatingEventsAnalysis = {
  "technical-element-type": TechnicalElementTypes.INITIATING_EVENT_ANALYSIS,
  "technical-element-code": "IE",
  
  metadata: {
    version: "1.0",
    analysis_date: "2024-03-01",
    analyst: "John Smith",
    reviewer: "Jane Doe",
    approval_status: "APPROVED",
    scope: [
      "Full power operation",
      "Low power operation",
      "Shutdown states",
      "Refueling operations"
    ],
    limitations: [
      "Analysis based on final EBR-II configuration (1990-1994)",
      "Experimental test configurations not included",
      "Limited to internal events during normal operation"
    ],
    assumptions: [
      {
        statement: "Primary sodium pump coastdown characteristics follow measured data from 1986 tests",
        basis: "Validated through multiple flow tests",
        impact: "MEDIUM"
      },
      {
        statement: "Reactor protection system reliability based on EBR-II operational experience",
        basis: "30 years of operational data",
        impact: "LOW"
      }
    ]
  },
  
  applicable_plant_operating_states: [
    "POS-1-FULL-POWER",
    "POS-2-LOW-POWER",
    "POS-3-HOT-STANDBY",
    "POS-4-COLD-SHUTDOWN",
    "POS-5-REFUELING"
  ],
  
  identification: {
    master_logic_diagram: {
      method_id: "MLD-EBRII-001",
      version: "2.0",
      analyst: "John Smith",
      review_date: "2023-11-15",
      review_status: "APPROVED",
      supporting_documents: [
        "ANL/EBR-II/FSAR-1993",
        "ANL-7321 EBR-II System Design Descriptions"
      ],
      sources: new Set(["NUREG-1829", "EBR-II_FSAR"]),
      operating_states: new Set([OperatingState.POWER]),
      radionuclide_barriers: {
        "FUEL-CLADDING": {
          name: "Fuel Cladding",
          description: "SS316 cladding for metal fuel",
          failureModes: ["Overheating", "Mechanical Failure"]
        },
        "PRIMARY-BOUNDARY": {
          name: "Primary Sodium Boundary",
          description: "Primary tank and connected systems",
          failureModes: ["Leak", "Rupture"]
        }
      },
      safety_functions: {
        "REACTIVITY-CONTROL": {
          name: "Reactivity Control",
          description: "Control rod system and inherent feedback",
          systems: ["Control Rod System", "Reactor Protection System"]
        },
        "HEAT-REMOVAL": {
          name: "Heat Removal",
          description: "Primary and secondary sodium systems",
          systems: ["Primary Sodium System", "Secondary Sodium System"]
        }
      },
      systems_components: {
        /* Component details */
      },
      failure_modes: {
        /* Failure mode details */
      },
      initiators: {
        /* Initiator details from MLD */
      }
    },
    heat_balance_fault_tree: {
      /* HBFT details */
    },
    failure_modes_analysis: {
      /* FMEA details */
    }
  },
  
  initiators: {
    "IE-LOSP": {
      id: "IE-LOSP",
      uuid: "12345678-1234-5678-1234-567812345678",
      name: "Loss of Offsite Power",
      eventType: "INITIATING",
      frequency: 2.5E-1,
      category: InitiatingEventCategory.TRANSIENT,
      description: "Loss of offsite power to EBR-II site",
      uncertainty: {
        distribution: DistributionType.LOGNORMAL,
        parameters: {
          mean: 2.5E-1,
          errorFactor: 2.0
        },
        sources: ["EBR-II operational history", "Idaho site-specific grid data"],
        description: "Based on 7 events during EBR-II operational history",
        assessmentMethod: "Bayesian update of generic prior with plant-specific data"
      },
      group: "LOSS-OF-POWER",
      applicableStates: ["POS-1-FULL-POWER", "POS-2-LOW-POWER", "POS-3-HOT-STANDBY"],
      groupId: "LOSP-GROUP",
      plantExperience: [
        "1965 - Grid disturbance caused site blackout",
        "1975 - Transformer failure at substation",
        "1983 - Lightning strike caused temporary outage"
      ],
      genericAnalysisReview: "Compared with NUREG/CR-6890 offsite power reliability data",
      screeningStatus: ScreeningStatus.RETAINED,
      importanceLevel: ImportanceLevel.HIGH,
      identification_method: "MLD",
      identification_basis: [
        "Historical events at EBR-II site",
        "Generic nuclear industry data",
        "Electrical system analysis"
      ],
      operating_states: [OperatingState.POWER, OperatingState.STARTUP, OperatingState.SHUTDOWN],
      trip_parameters: {
        "UNDERFREQUENCY": {
          parameter: "Electrical Frequency",
          setpoint: 57.5,
          uncertainty: 0.5,
          basis: "Prevents damage to plant equipment"
        },
        "UNDERVOLTAGE": {
          parameter: "Bus Voltage",
          setpoint: 3600,
          uncertainty: 100,
          basis: "Ensures equipment operability"
        }
      },
      mitigating_systems: {
        "DIESEL": {
          system: "Emergency Diesel Generator",
          function: "Provide backup AC power",
          success_criteria: "Start and load within 30 seconds",
          dependencies: ["DC Power", "Starting Air", "Fuel Oil"]
        },
        "NATURAL-CIRC": {
          system: "Natural Circulation Cooling",
          function: "Core cooling",
          success_criteria: "Establish flow path for natural circulation",
          dependencies: ["Primary Sodium Boundary Integrity"]
        }
      },
      barrier_impacts: {
        "FUEL-CLADDING": {
          barrier: "Fuel Cladding",
          state: BarrierStatus.INTACT,
          timing: "No immediate impact",
          mechanism: "None if mitigating systems function"
        },
        "PRIMARY-BOUNDARY": {
          barrier: "Primary Sodium Boundary",
          state: BarrierStatus.INTACT,
          timing: "No immediate impact",
          mechanism: "None"
        }
      },
      module_impacts: {
        "PRIMARY-REACTOR": {
          module: "EBR-II Reactor",
          state: ModuleState.SHUTDOWN,
          timing: "Immediate reactor trip"
        }
      }
    },
    
    "IE-LFLOW-PRIM": {
      id: "IE-LFLOW-PRIM",
      uuid: "87654321-4321-8765-4321-876543210987",
      name: "Loss of Primary Sodium Flow",
      eventType: "INITIATING",
      frequency: 4.8E-2,
      category: InitiatingEventCategory.TRANSIENT,
      description: "Loss of forced flow in the primary sodium system",
      uncertainty: {
        distribution: DistributionType.LOGNORMAL,
        parameters: {
          mean: 4.8E-2,
          errorFactor: 2.5
        },
        sources: ["EBR-II operational history", "EM pump reliability data"],
        description: "Based on operational experience with electromagnetic pumps",
        assessmentMethod: "Bayesian update of prior distribution"
      },
      group: "LOSS-OF-FLOW",
      applicableStates: ["POS-1-FULL-POWER", "POS-2-LOW-POWER"],
      groupId: "LOF-GROUP",
      plantExperience: [
        "1967 - EM pump power supply failure",
        "1978 - Flow controller malfunction",
        "1982 - Partial loss of flow due to electrical disturbance"
      ],
      genericAnalysisReview: "Compared with FFTF and international EM pump experience",
      screeningStatus: ScreeningStatus.RETAINED,
      importanceLevel: ImportanceLevel.HIGH,
      identification_method: "MLD",
      identification_basis: [
        "Historical events at EBR-II",
        "EM pump failure analysis",
        "Primary system design review"
      ],
      operating_states: [OperatingState.POWER, OperatingState.STARTUP],
      trip_parameters: {
        "LOW-FLOW": {
          parameter: "Primary Flow",
          setpoint: 85,
          uncertainty: 2,
          basis: "Prevents excessive fuel temperatures"
        },
        "HIGH-TEMP": {
          parameter: "Core Outlet Temperature",
          setpoint: 950,
          uncertainty: 5,
          basis: "Prevents sodium boiling"
        }
      },
      mitigating_systems: {
        "SCRAM": {
          system: "Reactor Protection System",
          function: "Reactor shutdown",
          success_criteria: "Insert control rods within 1 second",
          dependencies: ["DC Power", "Control Rod Drive Mechanism"]
        },
        "NATURAL-CIRC": {
          system: "Natural Circulation Cooling",
          function: "Core cooling",
          success_criteria: "Establish flow path for natural circulation",
          dependencies: ["Primary Sodium Boundary Integrity"]
        }
      },
      barrier_impacts: {
        "FUEL-CLADDING": {
          barrier: "Fuel Cladding",
          state: BarrierStatus.INTACT,
          timing: "No immediate impact if scram successful",
          mechanism: "Overheating if scram fails"
        },
        "PRIMARY-BOUNDARY": {
          barrier: "Primary Sodium Boundary",
          state: BarrierStatus.INTACT,
          timing: "No immediate impact",
          mechanism: "None"
        }
      },
      module_impacts: {
        "PRIMARY-REACTOR": {
          module: "EBR-II Reactor",
          state: ModuleState.SHUTDOWN,
          timing: "Immediate reactor trip"
        }
      }
    },
    
    // Additional initiating events would be defined here...
  },
  
  initiating_event_groups: {
    "LOSP-GROUP": {
      uuid: "ABCDEF12-3456-78AB-CDEF-12345ABCDEF1",
      name: "Loss of Electrical Power Events",
      description: "Events resulting in loss of normal electrical power to the plant",
      member_ids: ["IE-LOSP", "IE-LOSW", "IE-LOSG"],
      grouping_basis: "All events result in loss of normal electrical power requiring similar mitigation",
      bounding_initiator_id: "IE-LOSP",
      shared_mitigation_requirements: [
        "Emergency Power System",
        "Natural Circulation Cooling",
        "Reactivity Control System"
      ],
      challenged_safety_functions: ["REACTIVITY-CONTROL", "HEAT-REMOVAL"],
      applicable_operating_states: ["POS-1-FULL-POWER", "POS-2-LOW-POWER", "POS-3-HOT-STANDBY"],
      risk_importance: ImportanceLevel.HIGH
    },
    
    "LOF-GROUP": {
      uuid: "FEDCBA98-7654-32FE-DCBA-987654321ABC",
      name: "Loss of Flow Events",
      description: "Events resulting in reduction or loss of primary sodium flow",
      member_ids: ["IE-LFLOW-PRIM", "IE-LFLOW-PART", "IE-LFLOW-BLOCK"],
      grouping_basis: "All events result in reduced core cooling requiring similar mitigation",
      bounding_initiator_id: "IE-LFLOW-PRIM",
      shared_mitigation_requirements: [
        "Reactor Protection System",
        "Natural Circulation Capability",
        "Secondary Heat Removal System"
      ],
      challenged_safety_functions: ["HEAT-REMOVAL"],
      applicable_operating_states: ["POS-1-FULL-POWER", "POS-2-LOW-POWER"],
      risk_importance: ImportanceLevel.HIGH
    },
    
    // Additional initiating event groups would be defined here...
  },
  
  quantification: {
    "IE-LOSP": {
      event_id: "IE-LOSP",
      quantification: {
        mean: 2.5E-1,
        unit: FrequencyUnit.PER_YEAR,
        uncertainty: {
          distribution: DistributionType.LOGNORMAL,
          parameters: {
            mean: 2.5E-1,
            errorFactor: 2.0
          }
        },
        dataSources: [
          {
            name: "EBR-II Operational History",
            reference: "ANL-EBR-II-OPER-1994",
            description: "Compilation of EBR-II operational events 1964-1994"
          },
          {
            name: "Idaho Site Electrical Grid Data",
            reference: "INL-GRID-2010",
            description: "Historical data on grid reliability at Idaho National Laboratory site"
          }
        ],
        method: "BAYESIAN",
        bayesianUpdate: {
          priorDistribution: {
            type: DistributionType.LOGNORMAL,
            parameters: {
              mean: 3.0E-1,
              errorFactor: 3.0
            }
          },
          evidence: {
            events: 7,
            exposureTime: 30 // years
          },
          posteriorDistribution: {
            type: DistributionType.LOGNORMAL,
            parameters: {
              mean: 2.5E-1,
              errorFactor: 2.0
            }
          }
        }
      },
      data_exclusion_justification: "Events prior to 1965 were excluded due to significant changes in the site electrical distribution system",
      sensitivity_studies: [
        {
          parameter: "Grid Recovery Time",
          range: [0.5, 24], // hours
          results: "Core damage frequency is sensitive to recovery times longer than 4 hours",
          insights: "Procedures for extended loss of power should be prioritized"
        }
      ]
    },
    
    "IE-LFLOW-PRIM": {
      event_id: "IE-LFLOW-PRIM",
      quantification: {
        mean: 4.8E-2,
        unit: FrequencyUnit.PER_YEAR,
        uncertainty: {
          distribution: DistributionType.LOGNORMAL,
          parameters: {
            mean: 4.8E-2,
            errorFactor: 2.5
          }
        },
        dataSources: [
          {
            name: "EBR-II EM Pump Performance Records",
            reference: "ANL-EBR-II-PUMPS-1990",
            description: "Performance and failure data for EBR-II electromagnetic pumps"
          },
          {
            name: "International EM Pump Experience",
            reference: "IAEA-TECDOC-1668",
            description: "Operating experience with electromagnetic pumps in sodium-cooled reactors"
          }
        ],
        method: "BAYESIAN",
        bayesianUpdate: {
          priorDistribution: {
            type: DistributionType.LOGNORMAL,
            parameters: {
              mean: 7.0E-2,
              errorFactor: 5.0
            }
          },
          evidence: {
            events: 3,
            exposureTime: 30 // years
          },
          posteriorDistribution: {
            type: DistributionType.LOGNORMAL,
            parameters: {
              mean: 4.8E-2,
              errorFactor: 2.5
            }
          }
        }
      },
      other_reactor_data_justification: "Data from FFTF and Phenix reactors was used with adjustment factors to account for differences in pump design and operating conditions",
      fault_tree_details: {
        model_id: "FT-LFLOW-PRIM-001",
        top_event: "Loss of Primary Sodium Flow",
        modifications: [
          "Added common cause failure of EM pump power supplies",
          "Updated failure rates based on EBR-II specific data"
        ]
      }
    },
    
    // Additional quantification details would be defined here...
  },
  
  screening_criteria: {
    frequency_criterion: 1.0E-7,
    damage_frequency_criterion: 1.0E-8,
    basis: "Consistent with ASME/ANS RA-S-1.4-2021 requirements",
    screened_out_events: [
      {
        event_id: "IE-LSODIUM-LARGE",
        reason: "Frequency below screening threshold",
        justification: "Detailed structural analysis shows frequency < 1E-7/year for catastrophic primary tank failure in pool-type design"
      },
      {
        event_id: "IE-METEOR",
        reason: "Frequency below screening threshold",
        justification: "Site-specific analysis shows frequency < 1E-8/year for damaging meteorite impact"
      },
      {
        event_id: "IE-FIRE-MULT",
        reason: "Subsumed by more limiting event",
        justification: "Multiple fires scenario is bounded by the large facility fire initiator (IE-FIRE-LARGE) in terms of both consequences and mitigation requirements"
      }
    ]
  },
  
  insights: {
    key_assumptions: [
      "Natural circulation cooling capability is maintained following all initiating events that challenge forced cooling",
      "Inherent reactivity feedback mechanisms function as designed in all applicable scenarios",
      "Sodium leak detection systems can detect leaks greater than 10 gpm within 30 minutes"
    ],
    sensitivity_studies: {
      "NATURAL-CIRC": {
        parameter: "Natural circulation effectiveness",
        range: [0.7, 1.0], // Fraction of design capability
        results: "Core damage frequency varies by factor of 3.5 across range",
        insights: "Natural circulation effectiveness is critical for managing loss of flow events"
      },
      "SODIUM-LEAK-DETECT": {
        parameter: "Sodium leak detection time",
        range: [5, 60], // minutes
        results: "Early detection is critical for limiting sodium fire consequences",
        insights: "Improved detection systems could significantly reduce risk from sodium leaks"
      }
    },
    dominant_contributors: [
      "Loss of offsite power with failure of emergency power",
      "Loss of flow events with failure of natural circulation",
      "Sodium leaks with delayed detection and fire suppression"
    ],
    uncertainty_drivers: [
      "Limited operational experience with severe sodium leaks",
      "Uncertainty in natural circulation performance under various conditions",
      "Uncertainty in inherent reactivity feedback for beyond design basis conditions"
    ]
  },
  
  documentation: {
    processDescription: "The initiating event analysis for EBR-II employed a systematic approach including master logic diagram development, hazard evaluation, and operating experience review to identify, group, and quantify initiating events specific to sodium-cooled fast reactors.",
    inputSources: [
      "EBR-II Final Safety Analysis Report",
      "30 years of EBR-II operational records",
      "ANL sodium reactor safety research",
      "International experience with sodium-cooled reactors"
    ],
    appliedMethods: [
      "Master Logic Diagram",
      "Hazard and Operability Analysis",
      "Failure Modes and Effects Analysis",
      "Bayesian statistical analysis"
    ],
    resultsSummary: "The analysis identified 42 unique initiating events across 7 functional categories, which were grouped into 12 initiating event groups. Three initiating events were screened out based on frequency criteria.",
    functionalCategories: [
      "Reactivity Insertion Events",
      "Loss of Flow Events",
      "Loss of Heat Sink Events",
      "Loss of Primary Sodium Events",
      "Loss of Power Events",
      "Support System Failure Events",
      "External Hazard Events"
    ],
    plantUniqueInitiatorsSearch: "A detailed review of EBR-II's unique design features was performed, focusing on the pool-type primary system, electromagnetic pumps, and metal fuel characteristics. This included analysis of the inherent safety features and potential failure modes specific to the EBR-II design.",
    stateSpecificInitiatorsSearch: "Initiating events were identified for each operating state, considering the unique system configurations, barrier statuses, and vulnerability windows. Special attention was given to refueling operations and maintenance states with reduced inventory.",
    rcbFailureSearch: "A systematic evaluation of potential reactor coolant boundary failures was performed, considering the pool-type design, limited penetrations, and double-walled tank construction. The analysis included failure modes specific to sodium systems, including leak scenarios, freeze-seal failures, and cover gas system failures.",
    completenessAssessment: "Completeness was assessed through comparison with operational experience, other sodium reactor PRAs, and expert panel review. A structured approach verified coverage of all required initiating event categories and all identified safety functions.",
    screeningBasis: "Initiating events were screened based on frequency less than 1E-7/year with no special impact on risk, or being fully bounded by another initiator with more limiting characteristics.",
    groupingBasis: "Initiating events were grouped based on similar plant response characteristics, mitigation system requirements, and operator action needs. Each group has a defined bounding initiator that represents the most challenging conditions for analysis.",
    dismissalJustification: "Three observed events from EBR-II operating history were dismissed as non-representative based on subsequent design modifications that eliminated the failure mechanisms. These modifications were validated through testing prior to the end of EBR-II operations.",
    frequencyDerivation: "Initiating event frequencies were derived using a combination of EBR-II specific operating experience (30 reactor-years), generic data from other sodium fast reactors (where applicable), and Bayesian updating to develop plant-specific estimates when sufficient data existed.",
    quantificationApproach: "A hierarchical Bayesian approach was used to quantify initiating event frequencies, starting with generic prior distributions based on industry data, updated with EBR-II specific experience. For rare events with no operating experience, expert elicitation was employed following the SSHAC process.",
    dataExclusionJustification: "Early EBR-II operational data (1964-1967) was excluded from frequency calculations for selected initiating events related to control systems due to significant upgrades implemented in 1968 that fundamentally altered the failure mechanisms.",
    otherDataApplicationJustification: "Data from other sodium-cooled fast reactors (FFTF, Phenix) was applied with adjustment factors to account for design differences. The adjustment methodology considered power level differences, system design variations, and operational practices."
  },
  
  pre_operational_assumptions: [
    {
      statement: "For new sodium fast reactor designs based on EBR-II, the inherent reactivity feedback mechanisms are assumed to function similar to EBR-II demonstration tests",
      impact: "Directly affects the progression of unprotected (ATWS) scenarios following initiating events",
      treatmentApproach: "Conservative analysis using reduced feedback coefficients compared to EBR-II measurements",
      validationPlan: "Low-power physics testing program will measure actual reactivity coefficients during initial startup"
    },
    {
      statement: "For new designs, electromagnetic pump reliability is assumed equivalent to late-EBR-II experience with adjustment factors for design improvements",
      impact: "Affects frequency of loss of flow initiating events",
      treatmentApproach: "Applied uncertainty factors to reliability estimates and performed sensitivity studies on loss of flow frequency",
      validationPlan: "Reliability data collection program during commissioning and early operation"
    }
  ]
};
```

This sample implementation demonstrates how the schema comprehensively captures all aspects required by HLR-IE-D for a specific reactor type (EBR-II). The structure provides:

1. **Complete Documentation of Process and Methods**:
   - Detailed description of the analysis process
   - Input sources clearly identified
   - Methods explicitly documented
   - Results summarized comprehensively

2. **Functional Category Documentation**:
   - Sodium-specific functional categories identified
   - Events within each category listed
   - Unique characteristics of EBR-II reflected in categories

3. **Plant-Unique and State-Specific Search**:
   - Systematic approach to identifying EBR-II-specific initiators
   - Consideration of unique sodium systems and components
   - Operating state-specific initiators identified

4. **RCB Failure Search**:
   - Adapted to pool-type sodium reactor design
   - Unique failure modes for sodium boundary considered
   - Comprehensive analysis of potential failure locations

5. **Completeness Assessment**:
   - Verification against operational experience
   - Comparison with similar reactor analyses
   - Expert review process documented

6. **Screening and Grouping Basis**:
   - Clear criteria for screening decisions
   - Systematic approach to grouping
   - Consideration of EBR-II-specific characteristics

7. **Frequency Derivation and Quantification**:
   - Use of EBR-II-specific operational data
   - Application of appropriate generic data
   - Bayesian updating process documented

8. **Data Treatment Documentation**:
   - Justification for excluded data
   - Basis for using data from other reactor types
   - Adjustments for EBR-II-specific factors



This implementation provides a model for documenting initiating event analysis for sodium-cooled fast reactors, demonstrating that the schema fully satisfies the requirements of HLR-IE-D for this specific reactor type while providing the necessary traceability for regulatory review.# Initiating Event Analysis Documentation

## Table of Contents
- [1. IE-D1 Compliance](#1-ie-d1-compliance)
  - [1.1 Process Documentation (IE-D1)](#11-process-documentation-ie-d1)
  - [1.2 Functional Categories (IE-D1.a)](#12-functional-categories-ie-d1a)
  - [1.3 Systematic Search for Plant-Unique Initiators (IE-D1.b)](#13-systematic-search-for-plant-unique-initiators-ie-d1b)
  - [1.4 Approach for State-Specific Initiators (IE-D1.c)](#14-approach-for-state-specific-initiators-ie-d1c)
  - [1.5 Systematic Search for RCB Failures (IE-D1.d)](#15-systematic-search-for-rcb-failures-ie-d1d)
  - [1.6 Completeness Assessment Approach (IE-D1.e)](#16-completeness-assessment-approach-ie-d1e)
  - [1.7 Basis for Screening Out Initiators (IE-D1.f)](#17-basis-for-screening-out-initiators-ie-d1f)
  - [1.8 Basis for Grouping Initiators (IE-D1.g)](#18-basis-for-grouping-initiators-ie-d1g)
  - [1.9 Justification for Dismissal of Observed Events (IE-D1.h)](#19-justification-for-dismissal-of-observed-events-ie-d1h)
  - [1.10 Derivation of Initiating Event Frequencies (IE-D1.i)](#110-derivation-of-initiating-event-frequencies-ie-d1i)
  - [1.11 Quantification Approach (IE-D1.j)](#111-quantification-approach-ie-d1j)
  - [1.12 Data Exclusion Justification (IE-D1.k)](#112-data-exclusion-justification-ie-d1k)
  - [1.13 Other Reactor Data Application (IE-D1.l)](#113-other-reactor-data-application-ie-d1l)
- [2. IE-D2 Compliance](#2-ie-d2-compliance)
  - [2.1 Schema Support for Model Uncertainty Documentation](#21-schema-support-for-model-uncertainty-documentation)
  - [2.2 Example Model Uncertainty Documentation](#22-example-model-uncertainty-documentation)
- [3. IE-D3 Compliance](#3-ie-d3-compliance)
  - [3.1 Schema Support for Pre-operational Limitations](#31-schema-support-for-pre-operational-limitations)
  - [3.2 Example Pre-operational Assumptions Documentation](#32-example-pre-operational-assumptions-documentation)
- [4. Validation and Quality Assurance](#4-validation-and-quality-assurance)
  - [4.1 Schema Validation Functions](#41-schema-validation-functions)
  - [4.2 Traceability Features](#42-traceability-features)
- [5. Application to EBR-II](#5-application-to-ebr-ii)
  - [5.1 EBR-II Specifics](#51-ebr-ii-specifics)
  - [5.2 Sample Implementation for EBR-II](#52-sample-implementation-for-ebr-ii)

## 1. IE-D1 Compliance

### 1.1 Process Documentation (IE-D1)

The schema implements comprehensive process documentation through the `InitiatingEventDocumentation` interface:

```typescript
export interface InitiatingEventDocumentation {
    /** Description of the analysis process */
    processDescription: string;
    
    /** Input sources used in the analysis */
    inputSources: string[];
    
    /** Methods applied in the analysis */
    appliedMethods: string[];
    
    /** Summary of analysis results */
    resultsSummary: string;
    
    // Additional fields for detailed documentation requirements
    // ...
}
```

This interface is incorporated into the main `InitiatingEventsAnalysis` interface:

```typescript
export interface InitiatingEventsAnalysis extends TechnicalElement<TechnicalElementTypes.INITIATING_EVENT_ANALYSIS> {
    // Other fields...
    
    /**
     * Documentation of the Initiating Event Analysis process.
     * @remarks **HLR-IE-D**: The documentation of the Initiating Event Analysis shall provide traceability of the work.
     * @remarks **IE-D1**: DOCUMENT the process used in the Initiating Event Analysis specifying what is used as input, the applied methods, and the results.
     */
    documentation?: InitiatingEventDocumentation;
    
    // Other fields...
}
```

#### Sample Process Documentation

**Overall Process Description**:

The initiating event analysis for EBR-II follows a systematic approach aligned with RA-S-1.4-2021 requirements:

1. **Initial Definition Phase**: Review of design documentation, operating procedures, and similar reactor experience to establish the scope of analysis.
2. **Identification Phase**: Application of multiple complementary methods (MLD, HBFT, FMEA) to ensure comprehensive identification of all potential initiators.
3. **Screening Phase**: Evaluation of identified initiators against defined screening criteria.
4. **Grouping Phase**: Systematic grouping of initiators based on similar mitigation requirements.
5. **Quantification Phase**: Calculation of frequencies using appropriate data sources and methods.
6. **Documentation Phase**: Comprehensive documentation of the entire process, including assumptions, limitations, and insights.

This structured approach ensures the completeness and traceability required by HLR-IE-D.

### 1.2 Functional Categories (IE-D1.a)

The schema captures functional categories through the `InitiatingEventCategory` enum and related fields:

```typescript
/**
 * Enum representing categories of initiating events as specified in RA-S-1.4-2021.
 * These categories help in the organization and analysis of different types of events.
 * @remarks **IE-A5**: INCLUDE in the spectrum of initiating event challenges these general categories
 */
export enum InitiatingEventCategory {
    /** Equipment or human-induced events that disrupt plant operation with intact RCB */
    TRANSIENT = "TRANSIENT",
    
    /** Equipment or human-induced events causing a breach in the RCS */
    RCB_BREACH = "RCB_BREACH",
    
    /** Events in systems interfacing with RCS that could result in loss of coolant */
    INTERFACING_SYSTEMS_RCB_BREACH = "INTERFACING_SYSTEMS_RCB_BREACH",
    
    /** Special initiators not falling into standard categories */
    SPECIAL = "SPECIAL",
    
    /** Events caused by internal plant hazards */
    INTERNAL_HAZARD = "INTERNAL_HAZARD",
    
    /** Events caused by external hazards */
    EXTERNAL_HAZARD = "EXTERNAL_HAZARD",
    
    /** Events caused by at-initiator human failure events */
    HUMAN_FAILURE = "HUMAN_FAILURE"
}
```

Additional functional categorization is supported through the `documentation` field:

```typescript
export interface InitiatingEventDocumentation {
    // Other fields...
    functionalCategories: string[];
}
```

#### Sample Functional Categories Documentation

**Functional Categories for EBR-II**:

| Category | Description | Example Initiators |
|----------|-------------|-------------------|
| **Reactivity Insertion** | Events causing positive reactivity addition | Control rod withdrawal, gas bubble passage through core, fuel movement |
| **Loss of Flow** | Events reducing primary sodium flow | Primary pump trip, flow blockage, gas entrainment |
| **Loss of Heat Sink** | Events affecting heat removal capability | Intermediate heat exchanger (IHX) tube rupture, secondary sodium pump trip, loss of air flow to sodium-to-air heat exchangers |
| **Loss of Coolant** | Events resulting in sodium leakage | Primary boundary failure, instrument line break, cover gas system failure |
| **Loss of Power** | Events affecting electrical supply | Loss of offsite power, emergency diesel generator failure |
| **Fuel Handling** | Events during fuel handling operations | Fuel assembly drop, fuel transfer errors |
| **Support System Failures** | Events involving support systems | Instrument air failure, cooling water system failures |

Each functional category contains specific initiating events with similar phenomenology and mitigation requirements. The categorization ensures comprehensive coverage of the potential initiator space and facilitates systematic analysis.

### 1.3 Systematic Search for Plant-Unique Initiators (IE-D1.b)

The schema supports documentation of the search process through the identification methods:

```typescript
export interface InitiatingEventsAnalysis {
    // Other fields...
    
    /**
     * Methods used for identifying initiating events
     * @remarks **IE-A9**: Perform a systematic evaluation of each system down to the subsystem or train level...
     * @remarks **IE-A10**: Include initiating events resulting from multiple failures, including common cause failures and equipment unavailabilities due to maintenance or testing.
     * @remarks **IE-A12**: Interview at least one knowledgeable resource in plant design or operation to identify potential overlooked initiating events.
     * @remarks **IE-A13**: For operating plants, review operating experience for initiating event precursors and initiating events caused by human failures impacting later operator mitigation actions.
     */
    identification: {
        master_logic_diagram: MasterLogicDiagram;
        heat_balance_fault_tree: HeatBalanceFaultTree;
        failure_modes_analysis: FailureModesEffectAnalysis;
    };
}
```

Each identification method captures unique aspects of the search process:

```typescript
export interface MasterLogicDiagram extends IdentificationMethodBase {
    /* Fields for documenting the master logic diagram approach */
}

export interface HeatBalanceFaultTree extends IdentificationMethodBase {
    /* Fields for documenting the heat balance fault tree approach */
}

export interface FailureModesEffectAnalysis extends IdentificationMethodBase {
    /* Fields for documenting the FMEA approach */
}
```

#### Sample Plant-Unique Initiators Search Documentation

**Systematic Search Process for EBR-II Plant-Unique Initiators**:

1. **System-by-System Review**:
   - Conducted detailed reviews of each EBR-II system, including:
     - Primary Sodium System
     - Secondary Sodium System
     - Shutdown Cooling System
     - Cover Gas System
     - Instrumentation and Control Systems
     - Electrical Power Distribution Systems
     - Auxiliary Systems
   - For each system, analyzed to subsystem level using Master Logic Diagram approach.

2. **Sodium-Specific Phenomena Analysis**:
   - Identified initiators unique to sodium-cooled reactors:
     - Sodium-water reactions in steam generators
     - Sodium fires and their effects
     - Sodium freeze events in cold regions
     - Cover gas system interactions
     - Sodium void effects on reactivity

3. **Unique Design Feature Analysis**:
   - Analyzed EBR-II's unique pool-type design features:
     - Limited penetrations in primary tank
     - Passive safety characteristics
     - Natural circulation capabilities
     - Metal fuel behavior
     - Argon cover gas system

4. **Expert Elicitation Process**:
   - Conducted structured interviews with:
     - Original EBR-II designers (2)
     - Operations personnel (3)
     - Safety analysts familiar with sodium systems (2)
   - Facilitated identification of initiators not captured through other methods

5. **Operating Experience Review**:
   - Examined EBR-II operational history (1964-1994)
   - Reviewed experience from similar facilities (FFTF, Phenix, BN-600)
   - Identified plant-specific events not typically included in generic analyses

This multi-faceted approach ensured that plant-unique initiators specific to EBR-II's design and operational characteristics were comprehensively identified.

### 1.4 Approach for State-Specific Initiators (IE-D1.c)

The schema links initiating events to specific plant operating states:

```typescript
export interface ExtendedInitiatingEvent extends InitiatingEvent {
    // Other fields...
    
    /**
     * Plant operating states in which this initiating event can occur.
     * @remarks **HLR-IE-A**: The Initiating Event Analysis shall reasonably identify all initiating events for all modeled plant operating states ...
     */
    applicableStates?: PlantOperatingStateReference[];
}

export interface InitiatorDefinition extends ExtendedInitiatingEvent {
    // Other fields...
    
    /**
     * Operating states in which this initiator can occur
     * @remarks This property uses the OperatingState enum from plant-operating-states-analysis
     * to ensure type consistency across the codebase.
     */
    operating_states: OperatingState[];
}
```

Additionally, the documentation interface includes a field specifically for this purpose:

```typescript
export interface InitiatingEventDocumentation {
    // Other fields...
    stateSpecificInitiatorsSearch: string;
}
```

#### Sample State-Specific Initiators Documentation

**Approach for Identifying EBR-II State-Specific Initiators**:

The analysis identified initiating events specific to each plant operating state using a systematic matrix-based approach:

1. **Plant Operating State Definition**:
   - Defined 8 distinct EBR-II operating states:
     - POS-1: Full Power Operation (100%)
     - POS-2: Low Power Operation (0-40%)
     - POS-3: Hot Standby
     - POS-4: Primary System Hot, Reactor Shutdown
     - POS-5: Primary System Cold, Reactor Shutdown
     - POS-6: Refueling Configuration
     - POS-7: Maintenance Outage
     - POS-8: Primary System Drained

2. **State-Specific Parameter Analysis**:
   - For each POS, analyzed the unique configuration parameters:
     - Sodium temperature
     - Cover gas pressure
     - Component configurations
     - Decay heat levels
     - Available systems
     - Barrier status

3. **State-Transition Induced Events**:
   - Identified initiators that could occur during transitions between states
   - Example: Sodium freezing during cooldown (transition from POS-4 to POS-5)

4. **POS-Specific Vulnerability Assessment**:
   - For each POS, performed vulnerability assessments for:
     - Unique system alignments
     - Disabled safety functions
     - Reduced margin conditions
     - Maintenance configurations

5. **Documentation Structure**:
   - Created a systematic matrix mapping initiating events to applicable POSs
   - Example: Reactivity insertion events applicable to POS-1, POS-2, POS-3
   - Example: Fuel handling events applicable only to POS-6

This approach ensured comprehensive identification of initiating events for each modeled plant operating state, addressing the specific vulnerabilities and configurations unique to each state.

### 1.5 Systematic Search for RCB Failures (IE-D1.d)

The schema categorizes RCB failures as a distinct initiating event category:

```typescript
export enum InitiatingEventCategory {
    // Other categories...
    
    /** Equipment or human-induced events causing a breach in the RCS */
    RCB_BREACH = "RCB_BREACH",
    
    /** Events in systems interfacing with RCS that could result in loss of coolant */
    INTERFACING_SYSTEMS_RCB_BREACH = "INTERFACING_SYSTEMS_RCB_BREACH",
}
```

The documentation interface includes a specific field for this search process:

```typescript
export interface InitiatingEventDocumentation {
    // Other fields...
    rcbFailureSearch: string;
}
```

The schema also captures detailed information about barrier impacts:

```typescript
export interface InitiatorDefinition extends ExtendedInitiatingEvent {
    // Other fields...
    
    /**
     * Impact on radionuclide barriers
     * @remarks Uses the BarrierStatus enum from plant-operating-states-analysis
     */
    barrier_impacts: Record<string, {
        barrier: string;
        state: BarrierStatus;
        timing: string;
        mechanism: string;
    }>;
}
```

#### Sample RCB Failures Search Documentation

**Systematic Search for EBR-II RCB Failures**:

The analysis employed multiple complementary approaches to identify potential reactor coolant boundary (RCB) failures specific to EBR-II's design:

1. **Primary Tank Boundary Analysis**:
   - Comprehensive analysis of the primary tank boundary, considering:
     - Vessel penetrations (instrumentation, coolant inlet/outlet)
     - Cover gas boundary components
     - Primary tank welds and stress points
     - External impact scenarios

2. **Size-Based Categorization**:
   - RCB failures were categorized by size and location:
     - Small primary sodium leaks (<1 gpm)
     - Medium primary sodium leaks (1-50 gpm)
     - Large primary sodium leaks (>50 gpm)
     - Cover gas boundary failures
     - Instrument line breaks

3. **Location-Specific Challenge Assessment**:
   - For each potential failure location, analyzed:
     - Unique detection capabilities
     - Accessibility for isolation
     - Potential for sodium fires or sodium-concrete reactions
     - Impact on safety functions
     - Potential for common cause failures
     - Cavity flooding scenarios

4. **Interfacing Systems Analysis**:
   - Identified potential failures in systems interfacing with the primary sodium boundary:
     - Cold trap and purification systems
     - Sampling systems
     - Intermediate heat exchangers (sodium-to-sodium boundary)
     - Instrumentation and control systems

5. **Passive Failure Mechanisms**:
   - Analyzed long-term degradation mechanisms:
     - Thermal fatigue at temperature gradients
     - Material aging effects
     - Sodium corrosion mechanisms
     - Welds subject to thermal cycling

This comprehensive, systematic approach ensured identification of all credible RCB failure scenarios specific to EBR-II's design, with appropriate categorization based on size, location, and unique challenges to reactor-specific safety functions.

### 1.6 Completeness Assessment Approach (IE-D1.e)

The schema supports completeness assessment through validation functions and documentation:

```typescript
export const validateInitiatingEventsAnalysis = {
    // Other validation functions...
    
    validateCompleteness: (analysis: InitiatingEventsAnalysis): string[] => {
        const errors: string[] = [];
        // Check if all categories from IE-A5 are represented
        const categories = new Set(Object.values(analysis.initiators).map(ie => ie.category));
        const requiredCategories = [
            InitiatingEventCategory.TRANSIENT,
            InitiatingEventCategory.RCB_BREACH,
            InitiatingEventCategory.INTERFACING_SYSTEMS_RCB_BREACH
        ];
        
        for (const requiredCategory of requiredCategories) {
            if (!categories.has(requiredCategory)) {
                errors.push(`Required initiating event category ${requiredCategory} is not represented`);
            }
        }
        return errors;
    }
};
```

The documentation interface includes a field specifically for completeness assessment:

```typescript
export interface InitiatingEventDocumentation {
    // Other fields...
    completenessAssessment: string;
}
```

#### Sample Completeness Assessment Documentation

**Approach for Assessing Completeness and Consistency of EBR-II Initiating Events**:

The analysis employed a multi-faceted approach to ensure completeness of the initiating events list:

1. **Categorical Coverage Assessment**:
   - Verified coverage across all required initiating event categories from RA-S-1.4-2021
   - Ensured representation of EBR-II-specific categories relevant to sodium fast reactors
   - Validated that each category contained appropriate initiators

2. **Historical Experience Comparison**:
   - Benchmarked identified initiators against:
     - EBR-II operational experience (1964-1994)
     - Events from similar sodium-cooled reactors worldwide
     - Generic events applicable to all reactor types
   - Documented how each historical event is addressed in the current analysis

3. **Independent Review Process**:
   - Conducted structured peer reviews with:
     - Experts in sodium fast reactor technology
     - Former EBR-II operators
     - PRA specialists with non-LWR experience
   - Systematically addressed and resolved all review comments

4. **Comparison with Previous Safety Analyses**:
   - Compared identified initiators with:
     - EBR-II Safety Analysis Report
     - Special safety studies for EBR-II operations
     - Comparison with PRISM and other pool-type SFR designs
     - Other relevant sodium reactor PRAs
   - Documented justification for any differences

5. **Completeness Validation**:
   - Utilized formal validation techniques:
     - Hazard and operability studies (HAZOP)
     - "What-if" scenario development
     - Failure modes effects and criticality analysis (FMECA)
     - Automated validation using the schema's `validateCompleteness` function

6. **Documentation of Completeness**:
   - Created comprehensive mapping showing:
     - Coverage of required categories
     - Coverage of all plant operating states
     - Coverage of all identified hazards
     - Coverage of all safety functions that could be challenged
     - Coverage of all known sodium fast reactor phenomena

This systematic approach provides high confidence in the completeness and consistency of the identified initiating events with respect to previous experience, industry standards, and regulatory requirements.

### 1.7 Basis for Screening Out Initiators (IE-D1.f)

The schema captures screening criteria and documentation through dedicated interfaces:

```typescript
/**
 * Criteria for screening out initiating events
 * @remarks **IE-B7**: SCREEN OUT initiating events if they meet criteria
 */
export interface ScreeningCriteria {
    /** Frequency-based screening criterion */
    frequency_criterion: number;
    
    /** Damage frequency screening criterion */
    damage_frequency_criterion: number;
    
    /** Basis for screening criteria */
    basis: string;
    
    /** List of screened-out initiating events */
    screened_out_events: {
        event_id: string;
        reason: string;
        justification: string;
    }[];
}
```

This is incorporated into the main analysis interface:

```typescript
export interface InitiatingEventsAnalysis {
    // Other fields...
    
    /**
     * Screening criteria used to exclude initiating events
     * @remarks **IE-B7**: SCREEN OUT initiating events if they meet defined criteria
     */
    screening_criteria: ScreeningCriteria;
}
```

Each initiating event also has a screening status field:

```typescript
export interface ExtendedInitiatingEvent extends InitiatingEvent {
    // Other fields...
    
    /**
     * Basis for screening out this initiating event (if applicable).
     * @remarks **IE-D1**: DOCUMENT ... (f) the basis for screening out initiating events;
     */
    screeningBasis?: string;
    
    /**
     * Screening status of this initiating event
     * @remarks **IE-B7**: SCREEN OUT initiating events if they meet defined criteria
     */
    screeningStatus?: ScreeningStatus;
}
```

The documentation interface includes a specific field for screening documentation:

```typescript
export interface InitiatingEventDocumentation {
    // Other fields...
    screeningBasis: string;
}
```

#### Sample Screening Basis Documentation

**Basis for Screening Out EBR-II Initiating Events**:

The analysis applied the following screening criteria in accordance with RA-S-1.4-2021:

1. **Frequency-Based Screening**:
   - Initiating events with estimated frequency < 1E-7/year were screened out unless they led to severe consequences
   - Basis: Alignment with standard PRA practice and negligible contribution to risk

2. **Phenomenological Impossibility**:
   - Initiating events that are physically impossible given EBR-II's design were screened out
   - Required detailed technical justification for each screened event
   - Example: Large primary tank rupture was screened out based on inherent strength of pool-type design

3. **Subsumed Events**:
   - Initiating events wholly subsumed by another initiator (same impacts but less severe) were screened out
   - Required explicit mapping to the bounding initiator
   - Example: Small secondary sodium leaks were subsumed by medium secondary sodium leaks

4. **Screened Out Initiator Examples**:

| Initiator ID | Description | Screening Basis | Justification |
|--------------|-------------|-----------------|---------------|
| IE-SGTR-MULT | Multiple Steam Generator Tube Ruptures | Frequency | Calculated frequency of 3.2E-8/year based on tube failure data and conditional probability analysis |
| IE-PTLF-CAT | Catastrophic Primary Tank Large Failure | Phenomenological Impossibility | Analysis of pool-type design shows that catastrophic failure is not credible. Primary tank has significant margin (factor of >5) to ASME code limits, double-walled construction, and stress-relief design. |
| IE-IHXTR-SM | Small IHX Tube Rupture | Subsumed | Consequences and responses fully bounded by IE-IHXTR-MD (Medium IHX Tube Rupture). Both events have identical mitigation requirements, but medium rupture is more limiting. |

5. **Screening Validation**:
   - All screening decisions underwent independent peer review
   - Sensitivity analyses were performed on screened initiators to confirm negligible risk impact
   - Documentation includes explicit justification for each screening decision

This systematic screening approach ensures that analysis resources are focused on risk-significant initiating events while maintaining a technically defensible basis for each screening decision.

### 1.8 Basis for Grouping Initiators (IE-D1.g)

The schema captures grouping through dedicated interfaces:

```typescript
/**
 * Initiating event group defined by similar mitigation requirements
 * @remarks **IE-B1**: Group initiating events to facilitate definition of event sequences and quantification. Justify that grouping does not affect the determination of risk-significant event sequences.
 * @remarks **IE-B2**: Use a structured, systematic process for grouping initiating events.
 */
export interface InitiatingEventGroup extends Unique, Named {
    /** Description of the group */
    description: string;
    
    /** Member initiating events IDs */
    member_ids: string[];
    
    /** Basis for grouping */
    grouping_basis: string;
    
    /** The bounding (worst-case) initiator in the group */
    bounding_initiator_id: string;
    
    /** Shared mitigation requirements */
    shared_mitigation_requirements: string[];
    
    /** Safety functions challenged */
    challenged_safety_functions: SafetyFunctionReference[];
    
    /** Applicable operating states */
    applicable_operating_states: PlantOperatingStateReference[];
    
    // Other fields...
}
```

Each initiating event can reference its group:

```typescript
export interface ExtendedInitiatingEvent extends InitiatingEvent {
    // Other fields...
    
    /**
     * Grouping of initiating events with similar mitigation requirements.
     * @remarks **HLR-IE-B**: The Initiating Event Analysis shall group the initiating events so that events in the same group have similar mitigation requirements.
     */
    group?: string;
    
    /**
     * Unique identifier for the grouping of initiating events for analysis purposes.
     * @remarks **HLR-IE-B**: ...group the initiating events so that events in the same group have similar mitigation requirements...
     */
    groupId?: string;
}
```

The documentation interface includes a field specifically for grouping basis:

```typescript
export interface InitiatingEventDocumentation {
    // Other fields...
    groupingBasis: string;
}
```

#### Sample Grouping Basis Documentation

**Basis for Grouping and Subsuming EBR-II Initiating Events**:

The analysis employed a structured approach to group initiating events with similar mitigation requirements:

1. **Grouping Criteria**:
   - Initiating events were grouped based on:
     - Similar plant response
     - Similar mitigation systems required
     - Similar operator actions required
     - Similar phenomenological progression
     - Similar impact on safety functions

2. **Single vs. Multiple Reactor Plants**:
   - For EBR-II (single reactor plant), the grouping considered:
     - Impact on all operating states
     - Interactions with experimental facilities
     - Impact on fuel handling operations
     - Impact on connected support facilities

3. **Grouping Method**:
   - Systematic process involving:
     - Initial grouping based on phenomenological similarities
     - Verification of similar mitigation requirements
     - Selection of bounding initiator for each group
     - Validation that group frequency is properly represented
     - Sensitivity studies to confirm grouping doesn't mask risk insights

4. **Example Grouping Documentation**:

| Group ID | Group Name | Member Initiators | Bounding Initiator | Grouping Basis | Shared Mitigation Requirements |
|----------|------------|-------------------|-------------------|----------------|--------------------------------|
| LOHSNM | Loss of Heat Sink (Natural Circulation) | IE-LOHSM-PMP, IE-LOHSM-VLV, IE-LOHSM-HX | IE-LOHSM-HX | All events result in loss of heat removal capability with primary pumps running, requiring transition to natural circulation cooling mode. | 1. Reactor scram<br>2. Natural circulation establishment<br>3. Secondary system isolation<br>4. Long-term decay heat removal |
| RVITY | Reactivity Insertion Events | IE-RVITY-CROD, IE-RVITY-FLOW, IE-RVITY-FUEL | IE-RVITY-CROD | All events result in positive reactivity insertion challenging the reactivity control function. Control rod withdrawal bounds other events in terms of reactivity insertion rate. | 1. Reactor protection system actuation<br>2. Inherent reactivity feedback<br>3. Primary heat removal<br>4. Secondary heat removal |

5. **Validation of Grouping**:
   - Each grouping decision was validated through:
     - Thermal-hydraulic analysis confirming similar plant response
     - Verification that success criteria are consistent within group
     - Confirmation that the bounding initiator represents the most limiting conditions
     - Expert panel review of grouping adequacy

6. **Multi-Module Considerations**:
   - Although EBR-II is a single reactor, the analysis considered:
     - Impacts on connected experimental facilities
     - Potential for initiating events to affect multiple systems
     - Events affecting both the reactor and fuel handling systems

This systematic approach to grouping ensures efficient analysis while maintaining accuracy in risk insights. The explicit documentation of grouping basis provides transparency and traceability for regulatory review.

### 1.9 Justification for Dismissal of Observed Events (IE-D1.h)

The schema captures information about plant experience and observed events:

```typescript
export interface ExtendedInitiatingEvent extends InitiatingEvent {
    // Other fields...
    
    /**
     * List of plant-specific experience related to this initiating event (for operating plants).
     * @remarks **IE-A7**: For operating plants, REVIEW the plant-specific initiating-event experience to ensure that the list of challenges addresses plant experience for all modeled plant operating states.
     */
    plantExperience?: string[];
}
```

The documentation interface includes a field specifically for dismissal justification:

```typescript
export interface InitiatingEventDocumentation {
    // Other fields...
    dismissalJustification: string;
}
```

#### Sample Dismissal Justification Documentation

**Justification for Dismissal of Observed EBR-II Initiating Events**:

During EBR-II's operational history (1964-1994), several events occurred that were carefully evaluated for inclusion in the PRA model. The following observed events were ultimately dismissed with justification:

1. **1970 Primary Pump #1 Oscillations**:
   - **Event Description**: Oscillations in primary pump flow rate due to electromagnetic pump power supply instability
   - **Justification for Dismissal**: 
     - Power supply was redesigned in 1971 with improved feedback control
     - Post-modification testing showed complete elimination of oscillation behavior
     - Subsequent 23 years of operation with no recurrence
     - Design modification is incorporated in all modern EM pump designs

2. **1978 Secondary Sodium Leak in Steam Generator Building**:
   - **Event Description**: Small secondary sodium leak from valve packing
   - **Justification for Dismissal**:
     - Valve design was modified plant-wide in 1980 with improved packing materials qualified for sodium service
     - Leak detection systems were upgraded with increased sensitivity
     - Maintenance procedures were revised to address packing degradation mechanisms
     - Root cause analysis determined the failure was due to a manufacturing defect in a specific batch of valves, all of which were replaced

3. **1986 Control Rod Position Indication Failure**:
   - **Event Description**: False indication of control rod position leading to manual scram
   - **Justification for Dismissal**:
     - Instrumentation was upgraded to redundant, diverse position indication system
     - Software validation and verification processes were implemented
     - New technical specifications required cross-verification of position
     - Event was caused by a specific circuit board design flaw that was eliminated

4. **1990 Partial Loss of Plant Control System**:
   - **Event Description**: Partial loss of plant control system due to power supply failure
   - **Justification for Dismissal**:
     - Control system was completely redesigned with redundant power supplies
     - New uninterruptible power supply system installed
     - Design change eliminated single point vulnerability
     - Testing validated the effectiveness of the modifications

Each dismissed event underwent rigorous review to ensure that:
- The root cause was fully understood
- Corrective actions comprehensively addressed the failure mechanism
- Design or procedural changes were validated through testing
- Sufficient operational experience confirmed the effectiveness of the changes

Documentation for each dismissed event includes engineering analyses, modification packages, test results, and operational data supporting the conclusion that these specific event mechanisms are no longer credible for the current facility configuration.