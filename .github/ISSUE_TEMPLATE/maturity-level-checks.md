---
name: Virtual labs maturity level checks
about: Template for tracking the maturity levels of virtual labs
title: Virtual labs maturity level checks
labels: ''
assignees: ''

---
#### Maturity level 0
* Plan
  - [ ] There is an ambitious and realistic development plan for the virtual lab.
  - [ ] A timeline exists for the co-development, validation of the virtual lab and development of training material.
* Codebase
  - [ ] A new virtual lab is created.
* Version control
  - [ ] The codebase repository has version control (e.g. git).
* Security
  - [ ] Personal tokens for APIs do not end up in version control. Do not write your secrets in the codebase. Use [SecretsProvider](../../NaaVRE_Interface/#secrets-provider) or similar.
* Licensing
  - [ ] The virtual lab has a license.
* Documentation
  - [ ] The virtual lab has a nice name.
 
#### Maturity level 1
* Documentation
  - [ ] The virtual lab metadata is available outside the virtual lab.
    - [ ] Metadata is tracked by version control.
* Security
  - [ ] Personal tokens are not tracked by version control.
* Versioning
  - [ ] Versions of used software and libraries are pinned.
* Data
  - [ ] The data is ready for scientific experiments.
  - [ ] Data that is only read by the virtual lab is stored in an external catalogue.
* Codebase
  - [ ] The code executes without errors: The code can be executed without errors.
Currently, you can verify this by manually executing all cells in the notebook on a machine on which the code was not developed (to ensure no references are made to local resources).
  - [ ] The responsibility of each cell in the notebook is clear and can be described in a single sentence.
  - [ ] The coding style is consistent and follows a style guide e.g. For Python [PEP 8](https://peps.python.org/pep-0008/).
  - [ ] Parallel processing is applied where suitable.
  - [ ] There are clear errors when expected files and objects are not found.
  - [ ] External code use, such as command-line interface tools, are clearly labeled.
* Containerization
  - [ ] The notebook cells can be containerized.
* Workflow execution
  - [ ] The containerized cells can run without any modifications.
  - [ ] It is possible to give a demonstration of the virtual lab.
 
#### Maturity level 2
* User community
  - [ ] Other potential users have been identified.
* Data
  - [ ] All input data of the lab is FAIR.
* Metadata
  - [ ] All the fields of the metadata standard are present.
* Scenarios
  - [ ] The virtual lab can be used in multiple scenarios, i.e. both the parameters and datasets can be changed to suit experiments of different researchers.
* Documentation
  - [ ] There is a [user manual](../user_manual) and at least one domain scientist who was not involved in the development of the virtual lab has reviewed the user manual.
The coding experience of the reviewer of the user manual is similar to the coding experience of the intended user.
  - [ ] How to use the virtual lab on a different scenario is explained.
* Codebase
  - [ ]  Unit tests verify the behavior of used methods and libraries. There should be a testing guideline, which will be done in this issue [\#274](https://github.com/QCDIS/projects_overview/issues/274).
  - [ ]  The virtual lab reads, writes and exchanges data in a way that meets domain-relevant community standards. Recommendations for what standards to use are under investigation, see github issue [#281](https://github.com/QCDIS/projects_overview/issues/281).
  - [ ]  The code within cells is easily human-readable and others can easily modify it. If methods have side effects, this is clear to the user.
  - [ ]  The input and output of each cell is clear. It is both clear what the structure is (e.g. what data type is used) and what the data content is from a domain perspective.
* Workflow
  - [ ]  The duration of computation, memory usage, and power usage of the containers is acceptable. As there is currently no dashboard to monitor resource usage, contact the VLIC team for guidelines.
* Deployment
  - [ ] The virtual lab is publicly available.
* Infrastructure
  - [ ]  The infrastructure requirements for the workshop are known and the necessary infrastructure has been provided:
    - [ ]  The number of people taking part in a workshop.
    - [ ]  The random access memory and permanent storage usage of the virtual lab are known.
    - [ ]  The amount of processors the virtual lab uses is known.
