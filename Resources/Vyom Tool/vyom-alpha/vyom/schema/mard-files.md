# SAPHIRE File Types Reference

Based on available sources, this document provides a detailed description of SAPHIRE file types. File types are organized by functional category for easier reference.

## 1. Basic Event Files

*   **.BED**: **Basic Event names and descriptions**. These files contain the names and textual descriptions of the basic events used in your PRA model. You can modify these files using a text editor to enter or change the descriptions.

*   **.BEDA**: **Basic Event Names Descriptions (Alternate)**. This file contains alternate descriptions for basic events. The format includes the project name, the basic event's primary name, and the alternate description. This is useful for providing different ways of describing a basic event within the SAPHIRE project.

*   **.BEA**: **Basic Event Attributes**. These files contain additional information or attributes associated with the basic events. These can be extracted and loaded using the MAR-D module.

*   **.BEI**: **Basic event failure rates**. These files contain the probability or frequency of failure for each basic event, which is crucial for the quantification of your PRA model. Different calculation types can be associated with these rates.

*   **.BET**: **Basic Event Transformations Files**. These files are used to define transformations of basic events, specifying the project name, event names, transformation level, type (like AND, OR, ZOR), and the contributing basic events.

*   **.BEC**: **Basic Event Compound**. This file contains information for compound basic events. Compound events use external calculations (via DLLs) to determine their probability. The .BEC file format in SAPHIRE 8 includes the project name, the basic event name, a level, a type (like AND, OR, ZOR, or blank), and then the name of the plug-in library and the procedure within that library used for the calculation. Before version 8, compound information was stored in .BET files.

*   **.BECW**: **Basic Event Compound Wide**. This file type uses a "wide" format with one line per event for compound calculations. It includes fields for the type name, COM value, DLL name, procedure name, number of inputs, and the input values for the compound calculation.

*   **.BECAT**: **Basic Event Category**. This file assigns categories to basic events. The format includes the project name, followed by pairs of basic event names and their category names, and potentially a category level and label.

*   **.BECATW**: **Basic Event Category Wide**. This file uses a "wide" format with one line per event for category assignments. It includes fields for the category name, category identifier, and category item name.

*   **.BEG**: **Basic Event Grade**. This file specifies the grade or type of a basic event. The format includes the basic event name and a one-character grade (e.g., 'blank' for regular, 'S' for system-generated, 'V' for "virtual").

*   **.BEH**: **Basic Event HRA**. This file is used for information related to Human Reliability Analysis (HRA) for basic events. However, the specific format and content of this file are not detailed in the provided sources.

*   **.BER**: **Basic Event RASP CCF**. This file pertains to Common Cause Failure (CCF) data within the Risk Assessment of Severe Accident Phenomena (RASP) for basic events. In SAPHIRE 8, a calculation type 'R' is introduced to indicate a CCF object, replacing an older plug-in approach.

*   **.BERW**: **Basic Event RASP Wide**. This file uses a "wide" format with one line per event for Common Cause Failure (CCF) data. It includes fields for CCF type, model, staggered flag, separator, detail level, failure criteria, independent counts, independent event IDs and names, factor counts, and CCF factors.

*   **.BERN**: **Basic Event Rename**. This file provides a way to rename basic events. It includes fields for the current name, new name, and project name, allowing for the mapping between original and new event names.

*   **.BEMD**: **Basic Event Model Type Description**. This file contains the description for Basic Event Model Types. It would likely contain the project name, the name of the basic event model type, and its textual description.

*   **.BEMDA**: **Basic Event Model Type (Attribute)**. This file is used for attributes of Basic Event Model Types. It would probably include the project name, the basic event model type, and associated attribute information.

*   **.BEMT**: **Basic Event Model Type**. This file indicates the model type associated with a basic event.

## 2. Fault Tree Files

*   **.FTD**: **Fault Tree Names/Descriptions**. These files contain the names and descriptions of the fault trees within your SAPHIRE project. Fault tree descriptions and text can be entered into these flat files using a text editor and then loaded into SAPHIRE.

*   **.FTA**: **Fault Tree Attributes**. While the sources don't provide a detailed description, these files likely contain attributes or properties associated with the fault trees, possibly including uncertainty information. The sources suggest they are "usually not needed".

*   **.FTT**: **Fault Tree Textual Information**. These files contain descriptive textual information related to the fault trees. This can be entered using a text editor and then loaded into SAPHIRE.

*   **.FTL**: **Fault Tree Logic**. These files contain the logical structure of the fault trees, defining the relationships between gates and basic events. SAPHIRE can build the graphical representation of a fault tree from this logic file.

*   **.FTY**: **Fault Tree Post-processing Rules**. These files would contain rules that are applied after the fault tree is solved, for post-processing of the cut sets.

## 3. Event Tree Files

*   **.ETD**: **Event Tree Names/Descriptions**. These files contain the names and descriptions of the event trees in your project.

*   **.ETA**: **Event Tree Attributes**. This file contains attributes of event trees. This usually includes information specifying the correspondence to initiating events. The format includes the project name, the event tree name, and then various attribute fields.

*   **.ETL**: **Event Tree Logic**. These files contain the logical structure of the event tree, defining the top events and their branching probabilities. In SAPHIRE, the Event Tree Logic (.ETL) file is identical to the Event Tree Graphics (.ETG) file.

*   **.ETT**: **Event Tree Textual Information**. These files contain descriptive text associated with the event trees.

*   **.ETR**: **Event Tree Rules**. This file stores rules associated with event trees. These rules could be linking rules, recovery rules, or partition rules that define specific logic or actions within the event tree analysis. The format would likely include keywords like if, then, and endif to define the rule's logic.

*   **.ETY**: **Event Tree Partition Rules**. These files define the rules for partitioning the event tree sequences into different end states.

*   **.ETP**: **Event Tree Partition Rules**. This seems to be a repetition of the previous point, both referring to rules for partitioning event tree sequences.

*   **.EGD**: **Project Event Tree Group**. This file relates to grouping of event trees within a project.

*   **.EGI**: **Event Tree Group Information**. This file lists event tree groups and their event trees. It essentially provides a mapping of which event trees belong to which groups, allowing for organizational structure within the project.

## 4. Sequence Files

*   **.SQD**: **Sequence Names/Descriptions**. These files contain the names and descriptions of the accident sequences defined in your event trees. These are loaded prior to other sequence information files.

*   **.SQA**: **Sequence Attributes**. These files are needed to specify the relationships between sequences and FLAG SETS if those features are used. They can also contain other sequence-specific attributes like end state, number of minimal cut sets, mission time, etc.

*   **.SQL**: **Sequence Logic**. According to the sources, this file is "Not needed if event tree exists (can Link tree)". This suggests that the sequence logic can be derived from the event tree structure.

*   **.SQC**: **Sequence Cut Sets**. These files contain the minimal cut sets for each accident sequence. The format is similar to that of fault tree cut sets, listing the basic event combinations that lead to the sequence outcome. The sources note that these are "Generally not used since SAPHIRE can resolve cut sets".

*   **.SQY**: **Sequence Post-processing Rules**. Similar to fault trees, these files contain rules applied after the sequence cut sets are generated.

*   **.SQP**: **Sequence Partition Rules**. These files contain rules used to partition or group accident sequences based on certain criteria.

## 5. End State Files

*   **.ESD**: **End State Names/Descriptions**. These files contain the names and descriptions of the various end states defined in your PRA model. They should be loaded prior to other end state information files.

*   **.EST**: **End State Textual Information**. These files contain descriptive textual information about the end states.

*   **.ESC**: **End State Cut Sets**. These files contain the minimal cut sets that lead to specific end states.

*   **.ESI**: **End State Information**. This file contains information about the quantification method and passes for end states. The format includes the project name, end state name, and fields for the end state's default quantification method and number of passes. Some sources indicate it might be an undefined MAR-D file.

## 6. Gate Files

*   **.GTD**: **Gate information files (description, attributes)**. These files contain descriptions and potentially other attributes of the logic gates used in the fault trees.

*   **.GTA**: **Gate Attributes File**. This file lists the names, types (e.g., OR, AND), and alternate names for the gates used in the project.

## 7. Project Level Files

*   **.FAD**: **Project Names/Description File**. This file contains the overall project name and a brief description.

*   **.FAA**: **Project attributes**. This file contains attributes associated with the entire project, such as mission time, analyst information, etc.

*   **.FAT**: **Project text**. This file contains more extensive textual information or notes related to the project.

*   **.FAU**: **Project User Defined**. This file is used for user-defined project information. The specific content and format would be defined by the user to store project-specific data.

*   **.MTD**: **Project Model Types**. This file defines the model types used in the project. Model types in SAPHIRE allow for integrated model solving for different scenarios like random, seismic, or fire events. Basic events can be tied to specific model types.

*   **.PHD**: **Project Phase Model**. This file contains information about the phase model used in the project. SAPHIRE allows for defining phases within an analysis.

## 8. Special Purpose Files

*   **.HID**: This extension is not explicitly described in the provided sources. It might be related to histogram data, given that histograms are a feature of SAPHIRE for uncertainty analysis.

*   **.MARD**: This is a significant file type. A file with the **.MARD extension is used in SAPHIRE 8 to facilitate the loading and extraction of groups of PRA data**. This file acts as a reference to all other necessary files, which are typically stored in a subfolder created during extraction or needed for loading. This simplifies the process as you only need to open the one .MARD file. Previous versions of SAPHIRE used individual files for loading and extraction.

---

**Note**: Some file extensions lack complete documentation in the sources. These might be related to more specific or newer features of SAPHIRE, or they might be proprietary formats with limited public documentation. For a complete understanding of these file types, you might need to consult official SAPHIRE documentation or contact the software developers directly.