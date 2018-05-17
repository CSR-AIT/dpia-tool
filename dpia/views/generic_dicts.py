questions_dict = [
    'Does the program/change require you to collect any personal data, such as detailed household consumption data, organisational measurement data, etc.?',
    'Will the personal data be combined with other data from outside the program/change?',
    'Can the data collected become personal due to linkage by third parties?',
    'Will the program/change require you to collect personal data from other systems?',
    'Are you defining the conditions and the means of the processing operations (controller)?',
    'Are you conducting the processing on behalf of another organisation following their requirements (processor)?',
    'Have security and data protection requirements been defined between you and the processor/controller?',
    'Are the privacy impacts on consumers unknown to your organisation?',
    'Do consumers have to give up control of their personal data?',
    'Are consumers able to control which data are collected?',
    'Are they able to control their data after it has been collected?',
    'Is it expected that consumers will change their behaviour due to the fact their personal data (e.g. energy consumption or change of supply) will be collected (freedom of choice might be jeopardized)?',
    'Are you designing a new program or service within the smart grid use case or situation?',
    'Are you making significant changes to an existing smart grid use case or situation?',
    'Are you operating a system in production without a DPIA having been carried out?',
    'Are you facing a data breach?',
    'Are you selecting a cloud based service for the processing operations using personal data?',
    'Is the purpose of collecting the personal data not clear or not shared with the consumers?',
    'Will the personal data collected by the program/change be used for any other purposes, including research and statistical purposes?',
    'Is the purpose of the program/change inconsistent with community values of privacy?, Will the data be used for profiling?',
    'Will the use of the technology or purpose from the program/change raise questions and/or resistance from the consumers?',
    'Are there new (e.g. unevaluated) measures being applied in the design of the technology?',
    'Are the roles and responsibilities for processing the personal data unclear?',
    'Will the personal data processing be executed by a third party processor?',
    'Will the personal data be transferred to other organisations?',
    'Is there a legal obligation to conduct a Data Privacy Impact Assessment?',
    'Is the legal basis for processing of consumer data still unidentified?',
    'Is there a legal framework for the application or the smart grid use case?',
    'Do you anticipate that the public will have any privacy concerns regarding the proposed program or change?'
]

actors_dict = {
    1: [u'Producer', u'The Producer its role is to feed the output of its primary process, which is to produce energy, or rather transform energy into the energy grid.'],
    2: [u'Transmission System Operator', u'The role of TSO is to transport energy in a given area from centralized energy Producers to dispersed industrial energy consumers and distribution grid operators over its high voltage grid. Moreover, the TSO operates interconnectors with other high voltage grids of neighboring regions and countries.'],
    3: [u'Distribution System Operator (DSO)', u'The DSO is responsible for the cost-effective distribution of energy in a given area to and from end-users over the distribution grid and the connections to and from the transmission grid. The DSO ensures the long term ability of the distribution system to meet the demands for the distribution of energy.'],
    4: [u'Prosumer', u'The role of the Consumer transforms into a Prosumer. Residential end-users and small and medium-size enterprises become active up- and downloaders of energy. Prosumers offer their flexibility, resulting from Active Demand & Supply that they have ownership of, to the market. Active Demand and supply represents all energy-consuming or -producing appliances that that have the functionality to shift, increase or decrease its energy consumption or production.'],
    5: [u'Balance Responsible Party (BRP)', u'A Balance Responsible Party (BRP) is responsible for actively balancing supply and demand for its portfolio of Producers, Aggregators and Prosumers in the most economical way. The BRP forecasts the energy Demand & Supply of its portfolio and seeks the most economical solution for the requested energy to be supplied.'],
    6: [u'Supplier', u'The role of Supplier is to supply and invoice energy to its customers. The Supplier agrees commercial conditions with its customers for the   supply and procurement of energy.'],
    7: [u'Aggregator', u'The role of Aggregator consists of accumulating flexibility from Prosumers and their Active Demand & Supply, and selling this to the BRP and/or the DSO. It is the goal of the Aggregator to maximize the value of flexibility, taking into account both the customer needs, economical optimization and grid capacity.'],
    8: [u'ESCo', u'The ESCO offers auxiliary energy-related services to Prosumers but is not directly active in the energy value chain or the physical infrastructure itself. The ESCO may provide insight services as well as energy management services.']
}

ptargets_dict = {
    0: [u'Safeguarding quality of personal data.', u'Data avoidance and minimisation, purpose specification and limitation, quality of data and transparency are the key targets that need to be ensured.', [u'Collection exceeding purpose.', u'Combination exceeding purpose.', u'A lack of transparency for automated individual decisions.']],
    1: [u"Compliance with the data subject's right to object.", u"It must be ensured that the data subject's data is no longer processed if he or she objects. Transparency of automated decisions vis-a-vis individuals must be ensured especially in the case of profiling.", [u'Combination exceeding purpose.', u'Unlimited purpose.']],
    2: [u'Compliance with data retention requirements.', u'Retention of data should be for the minimum period of time consistent with the purpose of the retention or other legal requirements.', [u'Missing erasure policies or mechanisms; excessive retention periods.']],
    3: [u"Compliance with the data subject's right to be informed.", u'It must be ensured that the data subject is informed about the collection of his data in a timely manner.', [u'Undeclared data collection.', u'Lack of transparency.', u'Incomplete information.', u'A lack of transparency for automated individual decisions.']],
    4: [u'Legitimacy of processing personal data.', u'Legitimacy of processing personal data must be ensured either by basing data processing on explicit consent, contract, legal obligation, etc.', [u'Unlimited purpose.', u'Invalidation of explicit consent.', u'Non legally based personal data processing.']],
    5: [u'Legitimacy of processing sensitive personal data.', u'Legitimacy of processing sensitive personal data must be ensured either by basing data processing on explicit consent, a special legal basis, etc.', [u'Invalidation of explicit consent.', u'Non legally based personal data processing.']],
    6: [u"Compliance with the data subject's right of access to data, correct and erase data.", u"It must be ensured that the data subject's wish to access, correct, erase and block his data is fulfilled in a timely manner. Implementation of the right to be forgotten and the right to data portability should be encouraged.", [u'Lack of transparency.', u'Inability to execute individual rights (inspection rights).', u'Lack of access to personal data.', u'Inability to respond to requests for subject access, correction or deletion of data in a timely and satisfying manner.']],
    7: [u'Compliance with notification requirements.', u'Notification  about  data  processing,  prior  compliance checking and documentation are the key targets  need to be ensured. DPIA shall be considered as a determinant tool for this target.', [u'Prevention of objections.']],
    8: [u'Safeguarding confidentiality and security of processing.', u'Preventing  unauthorized  access,  logging  of  data processing, network and transport  security preventing accidental loss of data are the key targets that need to be ensured. Breach notification  procedure should be promoted.', [u'Unclear responsibilities for data processing.']],

}
