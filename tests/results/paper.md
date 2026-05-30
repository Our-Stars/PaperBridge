# DeepSeMS: revealing the hidden biosynthetic potential of the global ocean microbiome with a large language model

Tingjun Xu 1,2,6 , Yuwei Yang 1,6 , Ruixin Zhu 1 , Weili Lin 1 , Jixuan Li 3 , Yan Zheng 3 , Peng Zhang 4 , Guoqing Zhang 4 , Guoping Zhao 3,4,5 & Na Jiao 3

## Received: 15 March 2025

## Accepted: 27 March 2026

## Published online: xx xx xxxx

## Check for updates

Microbial-derived secondary metabolites (SMs) hold great therapeutic potential but are predominantly discovered from cultured species, representing only a fraction of microbial biodiversity. Advances in metagenomics have unveiled reservoirs of biosynthetic gene clusters (BGCs), but translating genomic sequences into precise chemical structures remains challenging owing to the structural complexity of cryptic BGCs and the context-dependent substrate tolerance and cross-reactivity of modular biosynthetic domains. Here we present DeepSeMS, a transformer-based large language model that accurately predicts secondary metabolite chemical structures from BGC sequences. By encoding biosynthetic genes as functional domains and leveraging a feature-aligned data augmentation, DeepSeMS outperformed existing methods and successfully generated chemically valid predictions for 96.38% of cryptic BGCs. Applying DeepSeMS to a global ocean metagenome, we characterized over 60,000 secondary metabolites, revealing chemical diversity, ecological specificity and considerable biomedical potential, especially as antibiotics. This study underscores the capability of deep learning-driven approaches in revealing hidden biosynthetic potential of Earth’s largest, yet largely unexplored, microbial ecosystem.

ecological niches 7 – 12 . Particularly, the global ocean, as the largest and arguably most diverse ecosystem on Earth, harbors an extraordinary diversity of microbial resources that remain largely underexplored and represents a promising resource for natural product discovery 13 . BGC discovery at the sequence level has advanced markedly over the past two decades, evolving from early reference-based approaches such as BLAST to rule-based algorithms and hidden Markov model (HMM)-based tools, including ClusterFinder 14 , and profile HMM-based tools such as antiSMASH 8 and PRISM 9 . These approaches enabled the systematic identification of BGCs across microbial genomes and laid the groundwork for genome mining. More recently, the introduction of deep learning frameworks, exemplified by DeepBGC 10 and

Secondary metabolites (SMs), particularly those produced by microbes, constitute a diverse and pharmacologically important class of natural compounds, with antimicrobial, anti-inflammatory, anticancer and metabolic therapeutic activities 1 , 2 . Their clinical applications are exemplified by widely used pharmaceuticals, such as antibiotics, statins and antitumor agents 3 , 4 . However, most currently available therapeutics originate from cultured microorganisms, representing less than 1% of global microbial diversity, leaving a vast reservoir of microbial-derived SMs unexplored 5 , 6 . Recent advances in metagenomic sequencing have substantially expanded access to uncultured and previously uncharacterized microbial species, uncovering extensive biosynthetic gene clusters (BGCs) and their potential to produce novel SMs across diverse

A full list of affiliations appears at the end of the paper. e-mail: rxzhu@tongji.edu.cn ; gqzhang@picb.ac.cn ; gpzhao@sibs.ac.cn ; najiao@fudan.edu.cn e-DeepBGC 15 , has further expanded the capacity to detect both known and cryptic BGCs. Despite these advances, directly mapping BGCs to their small-molecule products remains a major bottleneck in translating the exponential growth of genomic data into experimentally testable chemistry. This challenge is particularly relevant in the context of rising antimicrobial resistance, where alternative antibiotics are urgently needed but remain elusive. Tools such as antiSMASH 8 and PRISM 9 have incorporated curated reaction rules and domain architecture to support structure-level inference. However, predicting accurate chemical structures, especially for cryptic BGCs derived from metagenome-assembled genomes (MAGs) 11 , 12 , remains challenging. A major obstacle lies in the highly context-dependent and functionally promiscuous nature of biosynthetic enzymes 16 . For example, cytochrome P450 (CYP450), can catalyze diverse oxidative and rearrangement reactions, generating structurally distinct SMs 17 . Such enzymatic flexibilities, coupled with noncanonical domain organization and combinatorial complexity of tailoring domains in cryptic BGCs, often fall beyond the scope of predefined reaction rule libraries. Therefore, more flexible and predictive strategies are urgently needed to bridge the gap between sequence-based BGC discovery and the structural elucidation of their bioactive products. The advanced artificial intelligence (AI) technologies, particularly large language models (LLMs), have exhibited great capabilities to model complex sequential dependencies 18 , 19 . By conceptualizing chemical structure prediction as a language translation task, LLM-based approaches offer a potential strategy for mapping biosynthetic sequences to molecular structures 20 . Nevertheless, the translation of biological sequences into accurate chemical predictions via LLMs remains challenging. Biological sequences differ fundamentally from natural language in terms of feature recognition and functional constraints, and high-performance LLM training typically requires large, well-curated datasets, whereas experimentally verified BGC–SM pairs remain relatively limited and scarce 21 , 22 . To address these challenges, we developed DeepSeMS (Deep language model for Secondary Metabolite Structures prediction), a transformer-based framework specifically designed for automatically generating SM chemical sequences from input BGC sequences. BGCs were represented as functional-domain sequences to capture biosynthetic organization, and a feature-aligned data augmentation strategy was implemented to mitigate data scarcity. We evaluated DeepSeMS against existing approaches and assessed its performance on both characterized and cryptic BGC datasets. We further applied the framework to large-scale metagenomic resources from the global ocean to explore predicted chemical diversity and developed an accessible web server to facilitate community use.

Results The DeepSeMS framework Model overview . DeepSeMS is a transformer-based framework designed to predict SM chemical structures from BGC sequences (Fig. 1a , Supplementary Fig. 1 and Supplementary Table 1). BGC sequences are represented as sequential biological tokens (Pfam identifiers) and translated by the model into simplified molecular input line entry system (SMILES) strings describing the corresponding chemical structures. This sequence-to-structure framework enables the direct learning of relationships between biosynthetic logic and molecular outputs.

Sequence representation of BGCs and SMs . One key challenge in predicting SM structures from BGCs is defining an informative sequence representation 23 . We systematically evaluated multiple encoding strategies and found that functional-domain-based representation 10 provided the most effective balance between biochemical resolution and computational tractability (Fig. 1b ). Full-length amino acid sequences were often excessively long (frequently exceeding 50,000

tokens) and contained substantial redundancy, limiting efficient learning. By contrast, enzyme-level representations were substantially shorter (approximately 50 tokens per cluster) but lacked sufficient biochemical resolution. Functional-domain sequences, typically around 250 tokens, preserved key catalytic and architectural information while enabling efficient learning. These properties allowed DeepSeMS to capture relationships between domain organization and downstream chemical structure. For the output, SM structures were represented as SMILES strings 24 , enabling chemical structures to be modeled within a sequencelearning framework.

Feature-aligned data augmentation strategy . To overcome the limited number of experimentally characterized BGC–SM pairs in the MIBiG database 22 , we introduced a feature-aligned data augmentation strategy, conceptually equivalent to the scaffold-aware enumeration strategy that preserves core scaffold features while expanding chemical sequence diversity 21 , 25 . Specifically, we implemented a structural feature-aligned SMILES enumeration procedure (Fig. 1c and Supplementary Fig. 2). To validate the augmentation strategy, we randomly divided the initial dataset into a base training set (90%, n = 2,726) and an internal validation set (10%, n = 303). Models trained without augmentation generated chemically valid SMILES in 37.62% of cases (Supplementary Table 2). Randomized SMILES enumeration 26 increased validity to 78.88% but failed to recover target structures (0% exact recovery; mean Tanimoto coefficient 0.42 for structures and 0.41 for scaffolds relative to the ground truth). By contrast, feature-aligned SMILES augmentation achieved 76.24% validity while substantially improving structural fidelity, yielding 24.24% exact structure recovery and 49.78% scaffold recovery, with mean Tanimoto coefficients of 0.66 (structures) and 0.73 (scaffolds) (Supplementary Table 2). These results indicate that preserving scaffold-level features during SMILES enumeration is critical for chemical correctness and biosynthetic plausibility. Given this advantage, the full initial dataset was augmented using this strategy ( n = 55,903) and subsequently utilized for model training (Supplementary Fig. 3).

Ensemble modeling for structural diversity . Considering the complex biosynthetic landscape in which a single BGC can yield multiple structurally divergent SMs through alternative pathways and tailoring events, we implemented a tenfold cross-validation scheme and aggregated predictions across folds to capture biosynthetic variability (Supplementary Fig. 3). The ensemble framework produced multiple candidate structures per BGC and ranked them accordingly. Through this strategy, DeepSeMS achieved up to 85.71% chemical validity in generated SMILES strings and a mean structural similarity of 0.85 relative to reference compounds (Supplementary Table 3). DeepSeMS further provides physicochemical annotations (for example, molecular weight, heavy-atom count and synthetic accessibility) and novelty-related metrics for each prediction, enabling transparent prioritization of candidates for downstream experimental validation.

Accuracy and generalization on external datasets To comprehensively evaluate predictive accuracy and generalization capability of DeepSeMS, we curated two external test datasets. The ‘Known BGCs’ set ( n = 326), comprising experimentally verified BGC– SM pairs curated from the literature 11 , was used to evaluate the prediction accuracy. In parallel, the ‘Cryptic BGCs’ set ( n = 940), derived from bathypelagic MAGs lacking experimentally characterized SMs, was employed to assess the model’s performance beyond the characterized biosynthetic space. Performance was benchmarked against two widely used SM structure prediction tools, the SM structure prediction functions of antiSMASH 7 (ref. 12 ) and PRISM 4 (ref. 11 ).

## a

Feature identification

BGC

Data augmentation strategy Sequence representation

## b

Sequence of amino acids Sequence of Pfam identifiers Sequence of enzyme identifiers

BAP81855.1 BAP81857.1 PF05721.17 PF13561.10 PF00106.29 PF08659.14 PF01370.25 M T I E S K N Y P P I R R V N A S Q G S D A A Y Q

20 features; 50,000 tokens 1,020 features; 250 tokens 20,000 features; 50 tokens

Substrate specificity Linear assembly Tailoring and modifying

S

O

O

Information loss Tokens limitation Biosynthetic features and sequence context

## c

Randomized SMILES enumeration:

O 11 12

10

9

8

[5, 3, 4, 1, 11, 10, 19, 15, 17, 9, 2, 18, 12, 16, 7, 8, 13, 6, 14]

[2, 8, 14, 1, 16, 3, 10, 17, 9, 18, 13, 15, 5, 6, 11, 4, 7, 19, 12]

[4, 14, 5, 17, 1, 13, 9, 16, 8, 10, 19, 2, 3, 11, 12, 7, 15, 18, 6]

15

O 11 12

Randomized molecular graphs Randomized SMILES strings

13 14

10

3

16 17

OH 19

5

9

Structural features-aligned SMILES enumeration:

2

7

OH 6

4

O 18

8

1

O 11 12

13

10

5

7 9

[ 11, 10, 9, 7, 5, 13, 12 ]

Aligned SMILES strings Aligned molecular graphs Scaﬀold

**Figure 1 image:** assets/figures/fig_003_page_003.png

**Figure 1.** Fig. 1 | Overview of the DeepSeMS framework for SM structure prediction from BGCs. a , DeepSeMS is implemented based on transformer architecture. Input BGC sequences are processed through functional-domain identification (Pfam annotation) and embedded as tokenized sequence representations. A multilayer transformer with encoders-decoders self-attention modules learns to map BGC representations to corresponding SM structures (Supplementary Fig. 1). A chemical sequence decoder generates SMILES strings representing SM structures. A data augmentation strategy was applied to improve model robustness and generalizability. b , Comparison of three BGC sequence representation strategies: (1) amino acid sequences: biological primary residue strings of proteins (for example, MTIESK…), which are information-rich but contain limited task-specific signal and produce extremely long token sequences (≫10 4 ), imposing prohibitive O ( n 2 ) attention costs; (2) Pfam identifiers sequences: ordered functional-domain tokens, represented by Pfam IDs

## DeepSeMS model

Transformer architecture

O

Chemical sequence decoder

Self-attention mechanisms

Encoders Decoders

OH

OH

O

SM structure

```text
O=C1C=C(C)C(C=CC(=CC(=O)O)C)(O)C(C)(C)C1
```

## Sequence representation

O

OH

S

S

O

S

O

OH

OH

O

HO

OH

O OH OH O

O OH HO

## Data augmentation strategy

15

Sequence feature disorder

13 14

3

16 17

OH 19

5

7

2

OH 6

4

O 18

1

```text
C1(C=CC(C)=CC(O)=O)(O)C(C)=CC(=O)CC1(C)C
```

```text
C(C)(=CC(=O)O)C=CC1(O)C(C)(C)CC(=O)C=C1C
```

```text
C(C1(O)C(C)(C)CC(=O)C=C1C)=CC(C)=CC(O)=O
```

15

O 11 12

Feature blocks augmented

13 14

10

16 17

3

OH 19

5

9

2

OH 6 7

4

O 18

1

8

[ 11, 10, 9, 7, 5, 13, 12, 15, 3, 16, 2, 18, 4, 8, 14, 19, 6, 1, 17]

```text
O=C1C=C (C) C (C=CC(=CC(=O)O)C)(O) C (C)(C) C1
```

[ 11, 10, 9, 7, 5, 13, 12, 4, 19, 15, 16, 3, 17, 6, 18, 1, 8, 2, 14]

```text
O=C1C=C (C) C (C=CC(=CC(O)=O)C)(O) C (C)(C) C1
```

[ 11, 10, 9, 7, 5, 13, 12, 3, 4, 17, 1, 8, 18, 16, 2, 14, 19, 15, 6]

```text
O=C1C=C (C) C (C=CC(C)=CC(=O)O)(O) C (C)(C) C1
```

(for example, PF00106.29) derived from Pfam annotation, capturing substrate specificity, chain assembly and tailoring activities while preserving contextual information; (3) enzyme identifiers sequences: ordered enzyme identifiers (for example, GenBank accession BAP81855.1), which are coarser and lack explicit domain-level composition or ordering. Functional-domain sequences (~250 tokens) achieved the best balance between biochemical informativeness and computational efficiency. c , Two SMILES enumeration methods were compared to address the training data scarcity issue. Randomized enumeration generates syntactically diverse SMILES but disrupts structural coherence. Structural features-aligned enumeration preserves the molecular scaffold while varying peripheral groups, maintaining key chemical features and improving model performance. The details of SMILES enumeration methods are given in ‘Data augmentation’ in the Methods and Supplementary Fig. 2.

**Table 1.** Table 1 | Comparison of DeepSeMS model with existing methods on the ‘Known BGCs’ set ( n = 326)

| Method | Success
ratea | Structural
similarityb | Scafof ld
similarityc | Structure
recoveryd | Scafof ld
recoverye |
| --- | --- | --- | --- | --- | --- |
| antiSMASH 7 | 63.50% | 0.14 | 0.03 | 0.00% | 1.23% |
| PRISM 4 | 88.96% | 0.45 | 0.42 | 8.90% | 16.87% |
| DeepSeMS | 97.55%f | 0.60/0.71g | 0.63 | 41.10% | 53.68% |

## Method Success rate a Structural similarity b Scaffold similarity c Structure recovery d Scaffold recovery e

## antiSMASH 7 63.50% 0.14 0.03 0.00% 1.23%

## PRISM 4 88.96% 0.45 0.42 8.90% 16.87%

## DeepSeMS 97.55% f 0.60/0.71 g 0.63 41.10% 53.68%

a The percentage of BGCs for which at least one chemically valid SM structure was predicted.

b The mean structural similarity (Tanimoto coefficient) between the predicted SM structures and the ground truth. c The mean scaffold similarity between the predicted SM structures and the ground truth. d The percentage of BGCs with predicted structures that are chemically identical to the ground truth. e The percentage of BGCs with predicted scaffolds that are chemically identical to the ground truth. f The best results are bolded. g Utilizing consensus frequencies across the top ten model outputs, DeepSeMS attained a mean Tanimoto coefficient of 0.71 to the reference structures.

Prediction accuracy on the Known BGCs set . Among 326 BGCs, Deep- SeMS successfully generated at least one chemically valid SM structure for 318 BGCs, achieving a success rate of 97.55%, markedly exceeding the success rates of PRISM 4 (88.96%) and antiSMASH 7 (63.50%) (Table 1 and Supplementary Fig. 4a). In addition to broad coverage, DeepSeMS also achieved higher structural fidelity (Supplementary Fig. 4b,c). The generated structures exhibited substantially higher structural similarity to the ground truth, with mean Tanimoto coefficients of 0.60 for structures and 0.63 for scaffolds across diverse BGC types (Table 1 and Supplementary Fig. 4d). Notably, DeepSeMS predicted 134 (41.10%) chemically identical structures to the ground truth, a marked improvement over antiSMASH 7 (0.00%) and PRISM 4 (8.90%). In addition, more than half (53.68%) of the predicted structures preserved the exact scaffold architecture of their natural counterparts, substantially surpassing the scaffold recovery rates of antiSMASH 7 (1.23%) and PRISM 4 (16.87%). When cross-model consensus frequencies were used to prioritize candidates, the mean Tanimoto coefficient between the top-ranked predictions and the true reference structures increased further to 0.71. These results clearly indicate that DeepSeMS has greatly improved the accuracy of SMs structure prediction relative to current leading methods. To rigorously exclude data leakage and assess model generalization, we constructed stratified validation subsets from the ‘Known BGCs ’ set using progressively stricter sequence identity cutoffs (<90%, <75%, <60% and <50%) and SM structural similarity thresholds (Tanimoto coefficient <0.80 or <0.70) relative to the training set. These progressively stringent partitions enabled evaluation under progressively dissimilar conditions. Remarkably, DeepSeMS maintained consistent performance across all strata, achieving a 94.94% success rate and 37.97% scaffold recovery under the most stringent setting (sequence identity <50% and Tanimoto coefficient <0.70). These results indicate that the model’s predictions are not driven by memorization of training data but instead reflect true generalization to BGC–SM pairs dissimilar to those in the training set (Supplementary Table 4 and Supplementary Fig. 5).

Generalization on the Cryptic BGCs set . Building on the strong performance observed with known BGCs, we next evaluated the generalization on the ‘Cryptic BGCs’ set, which comprises largely uncharacterized gene clusters lacking experimentally validated SMs. DeepSeMS achieved a substantial improvement in mining SMs from these cryptic BGCs (Fig. 2 and Supplementary Table 5). Among 940 cryptic BGCs, DeepSeMS generated at least one chemically valid SM structure for 906 cryptic BGCs (96.38%). This represents an approximate 80% increase over antiSMASH 7, which predicted structures for only 159 BGCs (16.91%), and around a 50% increase over PRISM 4, which predicted structures for 203 BGCs (46.45%) (Fig. 2a ). DeepSeMS generated 4,678 chemically valid SM structures with 78.58% structure uniqueness, compared to 455 structures with 62.42% uniqueness for

PRISM 4 and 189 structures with 24.87% uniqueness for antiSMASH 7 (Fig. 2b ). Importantly, this performance is unlikely to result from data leakage: 97.87% of cryptic BGCs share <50% sequence identity with any training BGC, and stratified robustness tests across stricter identity cutoffs show stable predictive performance (Supplementary Fig. 6). Chemical space visualization based on Morgan fingerprints showed broader coverage of predicted SM chemical space by DeepSeMS (Fig. 2c ). This expansion is probably attributable to the model’s ability to learn and extrapolate underlying biosynthetic principles encoded within functional-domain sequences, enabling generation of structurally distinct compounds beyond the immediate training examples. The molecular weight distribution of DeepSeMS-generated structures aligned with the canonical 300–500 Da range characteristic of micro - bial SMs 2 , 27 (Fig. 2d ). Furthermore, the elevated synthetic accessibility scores reflected the inherent chemical complexity and synthetic feasibility of natural SM architectures (Fig. 2e ). A more uniform distribution of quantitative estimate of drug-likeness (QED) further indicated that DeepSeMS captured the broad structural and functional diversity typical of natural SMs (Fig. 2f ). Among BGC categories, DeepSeMS generated chemically valid SM structures for 38 of 39 BGC types, including common types such as nonribosomal peptide synthetases (NRPSs), polyketide synthases (PKSs) and terpenes, along with ribosomally encoded and post-translationally modified peptides (Supplementary Table 6). For 28 BGC types, including ectoine and type III PKSs (T3PKS), DeepSeMS achieved a perfect success rate of 100%. Remarkably, DeepSeMS exhibited robust performance on ‘hybrid’ BGCs (Supplementary Table 6), which encode compounds derived from the integration of two or more biosynthetic pathways within a single gene cluster 12 . In addition, Deep- SeMS successfully predicted SMs structures for clusters containing biosynthetic regions that do not fit into currently known categories, which indicates the strong generalization of DeepSeMS to BGCs from undescribed families. To further evaluate how DeepSeMS captures biosynthetic logic during structure generation, we investigated whether the predicted SMs reflect enzymatic functions encoded within their corresponding BGCs. As a representative case, we analyzed the cryptic cluster ‘mp-deep_mag-0578_000009.region001’, which encodes four classes of biosynthetic enzymes: dehydrogenase, phytoene synthase, α-glucosidase and glycosyl transferase. Previous studies have shown that dehydrogenase and phytoene synthase contribute to the biosynthesis of the polyunsaturated carbon backbone of phytoene-like molecules 28 , while α-glucosidase and glycosyl transferase would catalyze the reaction of glycosylation 29 , 30 . Among the predictions, five unique structures were identified after removing redundant candidates. These structures featured long-chain, unsaturated aliphatic hydrocarbon scaffolds with terminal glucoside moieties (Supplementary Fig. 7), consistent with transformations typically associated with these enzyme classes. These observations suggest that predicted structures reflect biosynthetic features encoded within the corresponding BGC sequences.

Hidden biosynthetic potential in ocean microbiome The global ocean harbors an extensive microbial diversity, much of which remains insufficiently characterized at the biosynthetic level 13 . To unlock this biosynthetic potential, we analyzed 45,894 BGCs derived from 27,139 MAGs within the Ocean Microbiomics Database (OMD) 31 , the most comprehensive resource of global ocean microbiomes. Using DeepSeMS, we predicted 60,327 unique SM structures associated with these BGCs, establishing a large-scale global ocean SM dataset for downstream structural and ecological analyses.

Molecular novelty and diversity of the global ocean SMs . Our analysis revealed extensive structural diversity among predicted SMs from the global ocean microbiome, spanning diverse chemical scaffolds

## a b

96.38% 906

90

Success rate No. BGCs

Structure uniqueness (%)

80

Success rate (%)

70

60

50

46.45% 203

40

30

20

16.91% 159

10

0

DeepSeMS PRISM 4 antiSMASH 7

## e f d

DeepSeMS

PRISM 4

0.5

antiSMASH 7

0.4

Density (%)

Density (%)

0.3

0.2

0.1

0

0

1,000

1,500

500

2,000

2,500

3,000

3,500

Molecular weight

**Figure 2 image:** assets/figures/fig_004_page_005.png

**Figure 2.** Fig. 2 | Comparison of DeepSeMS with existing methods on the cryptic BGCs test dataset. a , The bars represent the success rates of DeepSeMS, PRISM 4 and antiSMASH 7 with the number of BGCs annotated below each bar. The success rate is defined as the percentage of BGCs for which a method generates at least one chemically valid SM structure. b , The bars show the structure uniqueness of DeepSeMS, PRISM 4 and antiSMASH 7, with the number of unique SM structures annotated below. Structure uniqueness is defined as the proportion of nonredundant SM structures among all predictions, reflecting the structural

and ecological specificities. To quantify the molecular novelty of the generated global ocean SMs, we defined a ‘molecular novelty score’ (molecular NS; see ‘Model evaluation metrics’ in the Methods), calculated as the normalized inverse of the maximum structural similarity to the structures of known SMs in the MIBiG database. The distribution of molecular NS illustrated that most predicted SMs ( n = 60,201) from the global ocean microbiome were structurally dissimilar to previously characterized molecules (Fig. 3a ). Specifically, 97% of the global ocean SMs exhibited no close similarity to MIBiG compounds. This divergence was also evident at higher abstraction levels: 69% contained Murcko scaffolds absent from the reference dataset and 58% exhibited shapes, reflecting distinct two-dimensional scaffold connectivity, not represented in known compounds (Fig. 3b,c ). Furthermore, microbial communities across global oceans exhibited uniformly high molecular distinctiveness, with over 96% predicted SMs showing no close similarity to MIBiG compounds (Fig. 3d and Supplementary Table 7). The Arctic Ocean contributed the largest number of SMs (20,592), whereas the North Atlantic Ocean showed a higher proportion of shapes not represented in the reference dataset (61%). Distinct regional patterns were observed in SM structural uniqueness and diversity (Fig. 3e ). Specifically, the Arctic Ocean harbored the highest proportions of unique SMs (72%) absent from other oceans, whereas the Southern Ocean exhibited the greatest overall SM diversity (63%). Further analysis of ecological specificities revealed that environmental factors influence biosynthetic capacity (Supplementary Fig. 8). SMs sourced from the abyssopelagic layer (>4,500 m) and low-oxygen ( < 100 µmol kg −1 ) and medium-low temperature (~5–15 °C) habitats showed higher molecular NS values and greater structural diversity.

## c

DeepSeMS PRISM 4 antiSMASH 7

78.58% 4,678

Uniqueness No. structures

70

40

60

62.42% 455

20

50

PC 2

40

0

30

–20

24.87% 189

20

–40

10

0

DeepSeMS PRISM 4 antiSMASH 7

–60 60 40 20 0 –20 –40

PC 1

DeepSeMS

DeepSeMS

5

PRISM 4

PRISM 4

5

antiSMASH 7

antiSMASH 7

4

4

Density (%)

3

3

2

2

1

1

0 0 2 4 6 8

0 0 0.2 0.4 0.6 0.8 1.0

QED

Synthetic accessibility

diversity of a method’s predictions. c , The chemical space of the predicted SM structures visualized using the first two principal components (PC 1 and PC 2) of molecular fingerprints. Each point represents one predicted structure, colored by method. d , Kernel density estimates of molecular weight distributions of predicted SM structures. e , Distribution of synthetic accessibility (measured by synthetic accessibility score) of predicted SM structures by each method. f , Distribution of QED (quantitative estimate of drug-likeness) of predicted SM structures by each method.

Elemental composition analyses revealed systematic variation in oxygen, nitrogen and carbon contents of the global ocean SMs across gradients of oceanic depth, oxygen concentration and temperature, suggesting structural adaptation to diverse marine ecological conditions. Specifically, we found that the prevalence of PKS BGCs in deep ocean microbiomes correlated with a higher oxygen content of the SM molecules. However, the warmer and oxygen-rich surface water showed a lower nitrogen content and higher carbon content of the SM molecules, consistent with reduced proportions of NRPS and increased proportions of terpenes BGC types.

Biomedical application potential of the global ocean SMs . The discovery of structurally diverse SMs and previously uncharacterized BGCs within the global ocean microbiome presents opportunities for biomedical applications (Fig. 4 ). To assess their therapeutic potential, particularly as antibiotics, we implemented a structure-based virtual screening focusing on predicted SM substructures associated with established antibiotic properties, including β-lactams, aminoglycosides, tetracyclines, oxazolidinones, chloramphenicols, macrolides, ansamycins and quinolones. This screening uncovered 7,554 unique predicted SMs containing at least one antibiotic-associated structural motif (Fig. 4a ). These candidate compounds span multiple antibacterial mechanisms of action, including inhibition of bacterial cell wall, protein, RNA and DNA synthesis. Notably, many of these SMs possess side chains or substituents structurally distinct from those found in currently approved antibiotics, which may warrant further investigation in the context of resistance mechanisms. Together, these results indicate that the global ocean SM repertoire represents a

## a

3.0

2.5

2.0

Density (%)

1.5

1.0

0.5

0 0 20 40 60 80 100

Molecular NS

## d

## e

70

72

Diversity in the ocean province (%) Specialty in the global ocean (%)

60

53

50

43

40

35

35

30

32

20

10

0

Arctic Ocean South Pacific North Atlantic South Atlantic Indian Ocean North Pacific Mediterranean Red Sea Southern Ocean

**Figure 3 image:** assets/figures/fig_001_page_006.png

**Figure 3.** Fig. 3 | Molecular novelty and diversity of the global ocean SMs. a , Distribution of molecular NS for predicted global ocean SMs. The molecular NS was calculated from the maximum structural similarity between each predicted SM and compounds in the MIBiG database. b , A schematic illustrating three hierarchical levels of structural abstraction: molecular structure, scaffold (core framework) and shape (two-dimensional connectivity and topology of the scaffold). These levels were used to evaluate structural similarity and diversity. c , Pie charts showing the percentage of SMs classified as structurally dissimilar to MIBiG

substantial resource for antibiotic discovery, including potential leads targeting antibiotic-resistant pathogens such as multidrug-resistant Gram-negative pathogens 32 .

## b

O O

S

NH 2

N N

F F

N N

F

Structure Scaﬀold Shape

## c

## 69% 60% 97% 6 69% 58%

## 9

Novel structures Novel shapes Novel scaﬀolds

Arctic Ocean (20,592) South Pacific Ocean (16,523) North Atlantic Ocean (11,458) South Atlantic Ocean (11,223) Indian Ocean (8,940) North Pacific Ocean (8,440) Mediterranean Sea (4,111) Red Sea (3,117) Southern Ocean (1,925)

63

60

50

42 44 43

42 44

41

41

35

35

compounds at the structure, scaffold and shape levels among all predicted global ocean SMs. d , The geographical distribution of the global ocean SMs. The numbers in parentheses denote the total number of SMs identified in each province. The basemap was generated in R from GEBCO bathymetry data and Natural Earth coastlines. e , The molecular diversity and specialty of SMs across ocean regions. Light blue bars represent intraprovince diversity (percentage of unique SMs within a region), while dark blue bars indicate regional specialty (percentage of globally unique SMs originating from a given province).

In addition, we identified ectoine-producing BGCs as highly prevalent across the ocean microbiome. Ectoine is a compatible solute that protects microbes from extreme osmotic stresses 33 ,

## a

## SMs with antibiotic potential

O

O OH OH O

O

O

O HO

OH

O

N

HN

NH 2

O N

NH 2

OH

HO

OH

S

HO

O

O

HO

OH

O

O

O O

Cl

O O

OH

O

O

Cell wall Protein Protein Protein

HO

NH 2

OH

OH

OH

a1 (β-Lactams) a2 (Aminoglycosides) a3 ( Tetracyclines ) a4 ( Oxazolidinones )

OH HO

HO

O O OH

OH

O

OH HO

HO

HN O

OH

NH

O

OH

OH

O O

N + O

O

H 2 N

O N

OH

O

O - HO

HO

NH

O

O

HO

HO O O N O

O

OH

Cl

O

H N

NH O

N H

NH

OH

HO

Protein Protein RNA DNA

N H

Cl

OH

O

NH 2

O

O HO

a5 ( Chloramphenicols ) a6 ( Macrolides ) a7 ( Ansamycins ) a8 (Quinolones)

## b

## Natural cell protectant candidates

O

O

Biosynthetic pathways of ectoine

H N

H N

OH

OH

Biosyn_add ect_A ect_B ect_C

Biosyn_add

N

N

Natural cell protectant candidates

Ectoine

O

O

O

NH

HN

O

HN

O

N

HN

O

HO

OH

H 2 N

OH

N

N

OH

N

NH

N

OH

NH 2

OH

O OH

e1 (NS of 81.51) e2 (NS of 78.91) e3 (NS of 78.91) e4 (NS of 76.96) e5 (NS of 69.60)

O

O

OH H N

OH

O

O

HN

N

OH N

N

OH

OH

O

OH

HO

HN

N

HN N

N

O

e6 (NS of 69.31) e7 (NS of 68.84) e8 (NS of 67.53) e9 (NS of 61.25) e10 (NS of 42.48)

## c

## SMs with novel biosynthetic pathways

Biosynthetic pathways of undefined BGC families

Biosyn_add Biosyn_core Biosyn_core Biosyn_core

Biosyn_add

Innovative biomedical applications Unexplored microbial resources

NH 2

O

S S

N N

O

N O

O N H HN

HO

N H

N O

OH

OH N

n1 (NS of 98.44) n2 (NS of 97.73) n3 (NS of 95.77) n4 (NS of 95.37) n5 (NS of 94.87)

H N O

HO

N

OH

OH

HO

O H N O

HO

O S N

O

HO

N H

OH

n6 (NS of 94.12) n7 (NS of 94.06) n8 (NS of 93.83) n9 (NS of 93.53) n10 (NS of 93.46)

**Figure 4 image:** assets/figures/fig_005_page_007.png

**Figure 4.** Fig. 4 | Biomedical application potential of the global ocean SMs. a , Examples of antibiotic-like SMs ( a1 – a8 ) predicted from the global ocean microbiome, containing functional groups characteristic of major antibiotic classes, including β-lactams, aminoglycosides, tetracyclines, oxazolidinones, chloramphenicols, macrolides, ansamycins and quinolones. Functional moieties associated with known antibacterial activity are highlighted and mapped to their corresponding mechanisms of action, targeting bacterial cell wall, protein, RNA or DNA synthesis. b , The structures of the known natural cell protectant ectoine (top left) and top ten predicted SMs ( e1 – e10 ), ranked by molecular NS, identified from ectoine-associated BGCs in the global ocean microbiome. These candidates retain key pharmacophores of ectoine and are annotated with molecular NS.

The biosynthetic pathway (top middle) includes canonical ectoine biosynthesis enzymes (ect_A, ect_B and ect_C) and additional accessory enzymes (Biosyn_add), denoted by distinct color coding. c , Ten SMs ( n1 – n10 ) with high molecular NS values identified from undefined BGC families. The structures are annotated with the molecular NS. The biosynthetic origins are inferred from domain architecture of the corresponding BGCs, with Biosyn_core (dark blue) and Biosyn_add (light blue) representing core and auxiliary biosynthetic enzymes, respectively, as predicted by Pfam-based functional-domain annotations. While explicit reaction mechanisms are not available, the illustrated domain compositions provide a putative overview of biosynthetic logic underlying these metabolites.

## AI-powered tools for accelerating novel SM discovery

BGCs

## DeepSeMS web server

Genome mining of novel SMs from uncultivated microbes Exploration of various SMs from the global ocean microbiome

biosynthetic_region001.gbk

## Deep Ocean SM Exploration

antiSMASH job id: bacteria-6eb5fc6b-2f44-415f-97fc-3b5e07dcd29d

MF: C 38 H 60 N 12 O 10 MW: 844.97

87.65 67.98

QED: 0.23

SA: 0.12

59.63 64.88

Molecular properties

Prediction scores

**Figure 5 image:** assets/figures/fig_002_page_008.png

**Figure 5.** Fig. 5 | Schematic overview of the AI-powered tools for accelerating SMs discovery. DeepSeMS enables the prediction of SM structures directly from microbial BGCs, facilitating the discovery of structurally distinct compounds from uncultivated microbes. The DeepSeMS web server accepts annotated BGCs and outputs candidate SM structures with associated molecular properties, prediction scores, novelty assessments and inferred antibiotic activities. In addition, the global ocean SMs dataset, embedded as a built-in resource,

consistent with adaptation to bathypelagic environments. From ectoine biosynthetic pathways, 1,884 ectoine-related SMs were predicted, among which a subset (Fig. 4b ) retained key pharmacophoric features of canonical ectoine and exhibited relatively high molecular NSs. These structural analogs hold promise as next-generation natural cell protectants, with potential applications in cosmetics, medicine and biotechnology 34 , 35 . Furthermore, we characterized 587 SMs associated with undefined BGCs containing biosynthetic regions that do not fit into any documented category 12 . These SMs exhibited scaffolds and shapes not represented in the MIBiG reference dataset. The presence of such structural patterns in unclassified BGCs underscores the extent of biosynthetic regions that remain functionally uncharacterized. Specifically, four of the top ten SM structures with the highest molecular NS values (Fig. 4c ), namely n3 , n6 , n7 and n9 , were all traced to a single cryptic BGC within the MAG ‘BGEO_SAMN07136520_METAG_FKHEEFFA’, derived from a seawater sample collected in the North Atlantic Ocean. The corresponding MAG was taxonomically assigned to ‘ UBA7446 sp002478685 ’, and

NH 2 H 2 N H N

OH

O

N

O S O

O OH

NH

O

O HN

OH O O O

O

OH

OH

N O O

O NH HO

O O N H H 2 N

O

N

O

N H

NH 2

OH

OH

## DeepSeMS

O NH

HO

O O

HO

HO

HO

O

HO OH

NH 2 NH

HO

N H

H 2 N N

O HN

H 2 N

O

OH

SM structures

## Global ocean SMs

Arctic Ocean, Atlantic Ocean, Indian Ocean

Mediterranean Sea, Pacific Ocean, Red Sea, Southern Ocean

89.81

OH OH H 2 N

Aminoglycosides

OH

O S O O

O

Most similar known SM: cyanopeptolin

HO

H 2 N

Tetracyclines

β -Lactams

HO NH

HN O

O

O

NH

95.02

O

O

Oxazolidinones

O O N O

O NH O

O NH

Structural similarity: 0.31 Quinolones

O

H N

HN N

O

## Macrolides

OH N H 2 N

O

NH 2

Molecular novelties Antibiotic potentials

supports exploration of previously uncharacterized SMs from diverse marine environments, revealing cryptic biosynthetic potential across major oceanic provinces. Together, these tools provide a scalable solution for natural product mining from microbial genomes. MF, molecular formula; MW, molecular weight; SA, synthetic accessibility. The basemap was generated in R from GEBCO bathymetry data and Natural Earth coastlines.

emerges as a promising candidate for future bioprospecting of marine natural products.

AI-powered tools for accelerating SMs discovery To facilitate the application of DeepSeMS to microbial SMs discovery, we have deployed the model as a publicly accessible web server (Fig. 5 ) at https://biochemai.cstspace.cn/deepsems/ . Users can submit BGC annotation files generated by tools such as antiSMASH, DeepBGC or, alternatively, provide antiSMASH job IDs to obtain predicted SM structures. The web server returns ensemble-based predictions together with biosynthetic annotations, consensus frequencies, prediction scores, molecular visualizations and physicochemical properties. Functions for comparison with known compounds are provided to support the evaluation of structural distinctiveness and potential bioactivity. The results are accessible through persistent job links, enabling sharing and downstream analysis. To support exploration of the predicted metabolites generated in this study, we integrated the global ocean SM dataset as a built-in resource within the server. This repository includes BGCs identified from both annotation-based approaches and de novo predictions (via DeepBGC), thereby capturing cryptic biosynthetic potential. Users can browse this repository by geographic locations, marine environments and BGC types, with filtering and visualization options for the biosynthetic pathways, molecular NS values and predicted antibiotic potentials. For instance, querying cryptic NRPS BGCs from the Biogeotraces_GT15_GP13_TAN1109 sample set in the South Pacific Ocean returns five records. The top-ranked cluster originates from the MAG of bacterium ‘ Arctic96AD-7 sp002082305’, sampled from the bathypelagic layer (1,008 m; 4.94 °C; oxygen content of 200.4 μmol kg −1 ). The detailed result page displays five predicted SM structures associated with this BGC, two of which are predicted to exhibit macrolide-like antibiotic potential. Both the BGC and predicted structures can be downloaded for further research.

Discussion The ability to translate BGC sequences into plausible SM structures remains an important challenge in natural product research. In this work, DeepSeMS, a transformer-based LLM, highlights the potential of sequence-based generative models to connect microbial genomic information with chemical space. Rather than relying solely on predefined biosynthetic rules 36 , learning-based approaches may capture broader patterns of biosynthetic logic and therefore provide complementary hypotheses for exploring cryptic or poorly characterized BGCs 36 . This conceptual shift—from deterministic reconstruction to probabilistic generation—provides a scalable framework for translating microbial biodiversity into chemical diversity. Several methodological considerations illustrate broader implications for computational natural product discovery. Regarding the DeepSeMS framework, representing BGCs through functional-domain representations enabled the model to operate on biologically meaningful intermediate units rather than raw sequence tokens. This design suggests that biologically informed representations can balance sequence complexity with biosynthetic relevance, facilitating generative modeling while retaining interpretability. In addition, incorporating a structural feature-aligned augmentation strategy provided a mechanism for introducing chemical priors into training, thereby supporting structural coherence (for example, scaffold preservation) under limited-data conditions. The large-scale application to global ocean metagenomes illustrates how sequence-to-structure frameworks may assist in organizing predicted chemical diversity and prioritizing candidate metabolites for further study. The integration of such predictions into searchable repositories can support systematic exploration across ecological contexts. Notably, predicted molecules displaying antibiotic-like structural features underscore the potential relevance of generative approaches in identifying chemically diverse candidates for follow-up evaluation, particularly in the context of antimicrobial resistance 37 . These predictions, however, should be interpreted as hypothesis generating rather than definitive assignments. Beyond marine systems, DeepSeMS may be applicable to expanding metagenomic resources from human gut 38 , soil 39 and plant-associated microbiomes 40 , where microbial SMs have been implicated in ecological interactions and host phenotypes. For example, experimentally supported associations between gut bacterial BGCs and inflammatory bowel disease 41 , 42 underscore the importance of connecting biosynthetic loci to their molecular products, a step that predictive frameworks may help facilitate. Generative architectures may also inform future synthetic biology efforts 43 , 44 , although such applications remain prospective and dependent on experimental validation. Despite these opportunities, several limitations should be acknowledged. First, incomplete identification of biosynthetic domains, especially those with weak homology to known Pfam annotations, may result in fragmentary or inaccurate SM predictions. Second,

defining precise BGC boundaries remains challenging, particularly for cryptic or noncanonical clusters, and inaccurate boundaries may result in partial or nonrepresentative structures. In addition, training data remain limited to currently characterized BGC–metabolite pairs, which may bias predictions toward known biosynthetic chemistries and reduce extrapolation to underrepresented metabolite classes. Future efforts should strengthen the connection between computational prediction and experimental validation. Improvements in domain annotation and BGC boundary detection, together with integration of transcriptomic and metabolomic evidence, may help prioritize actively expressed pathways and increase confidence in predicted structures. Experimental validation through heterologous expression, targeted metabolomics and structural elucidation using tandem mass spectrometry (MS/MS) and NMR will be essential for assessing prediction accuracy and defining practical confidence ranges. Systematic benchmarking across diverse biosynthetic systems will further clarify where sequence-to-structure generative approaches are most reliable. As experimentally validated datasets continue to expand, iterative interaction between predictive modeling and empirical testing may progressively refine the scope and accuracy of such frameworks, positioning them as useful components of future natural product discovery workflows.

Methods Model construction Data preparation . Training dataset: the training dataset of DeepSeMS model was curated from MIBiG database (version 3.1, https://mibig. secondarymetabolites.org/ ) 22 . BGC sequences and their corresponding SM structures, represented as SMILES strings, were paired based on shared accession number between the MIBiG sequence files and annotation files. The final training dataset consisted of 3,029 one‑to‑one BGC–SM pairs, involved with 1,844 BGCs and 2,712 SM structures, respectively. Notably, 486 BGCs were associated with more than one structure. Structural issues in the SMILES strings, mainly incorrect valence states, mixture and stereochemical inconsistencies were identified by RDKit (version 2023.03.1, http://www.rdkit.org/ ) and corrected manually according to the MIBiG reference annotations. Sequence representation: for the source representation, BGC sequences were processed using Biopython (version 1.8.1, https:// biopython.org/ ) and HMMER (version 3.4, http://www.hmmer.org/ ) to identify biosynthetic features (Pfam identifiers) by searching functional domains against the Pfam 45 (version 36.0) database with a threshold of e-value <0.01. Functional-domain annotations, represented by Pfam identifiers, were used to encode the biosynthetic logic of each BGC. A total of 1,016 unique Pfam IDs were identified across the dataset. These domain features, together with four predefined special tokens ( 〈 PAD 〉 , 〈 BOS 〉 , 〈 EOS 〉 and 〈 UNK 〉 ), constituted a source vocabulary of 1,020 tokens for the LLM ( https://github.com/lab-of-biochemai/ DeepSeMS/blob/main/vocabs/bgc_features_vocab.csv ). The enzyme identifier was extracted from the protein_id information in the BGC gbk file supplied by the MIBiG database, corresponding to its GenBank accession. To reduce the complexity of molecular generation models and ensure syntactic validity, canonical SMILES representation was generated using RDKit by removing the stereochemical information. SM structures were tokenized as sequences of SMILES strings, yielding a target vocabulary of 35 distinct structural features (unique SMILES notations) for the LLM ( https://github.com/lab-of-biochemai/Deep- SeMS/blob/main/vocabs/smiles-vocab.pt ). External test dataset: we assembled two independent datasets to evaluate DeepSeMS: a ‘Known BGCs’ set to assess predictive accuracy and a ‘Cryptic BGCs’ set to evaluate extrapolation and generalization performance. The raw ‘Known BGCs’ set was derived from the curated repos - itory provided by the PRISM 4 authors 11 ( https://doi.org/10.5281/ zenodo.3985982 ). Sequence–structure pairs were prepared following the same procedures of structural and biosynthetic features annotation as for the DeepSeMS training dataset. Specifically, BGC sequences were annotated using antiSMASH 12 (version 7.0.0) with the ‘genefinding-tool’ of ‘prodigal’ and default parameters otherwise, ensuring consistent structural and biosynthetic feature annotation. To prevent data leakage, from the sequence level we excluded any BGC with >95% sequence identity or >80% coverage to the BGCs in training set by BLAST 46 and further excluded those with identical Pfam domain compositions. After these filters, 326 one‑to‑one BGC–SM pairs (326 BGCs corresponding to 276 unique SM structures) remained for the model accuracy evaluation, and this collection is hereafter referred as the ‘Known BGCs’ set. The ‘Cryptic BGCs’ set was sourced from the Malaspina Deep Metagenome-Assembled Genomes 47 ( https://malaspina-public.gitlab.io/malaspina-deep-ocean-microbiome/ ). Biosynthetic regions in MAGs were identified using antiSMASH 12 (version 7.0.0) with the ‘genefinding-tool’ of ‘prodigal’ and default parameters otherwise. Applying the same inclusion criteria as ‘Known BGCs’ set, we obtained a dataset of 940 cryptic BGCs for model evaluation of generalization ability. To detect hidden overlap with the training set and assess generalization into increasingly distant sequence and structural space, we evaluated the model performance on stratified partitions. For the ‘Known BGCs’ set, we created 12 partitions by crossing four sequence-identity cutoffs (<90%, <75%, <60% and <50%), defined as the maximum BLAST percent identity to any training BGC, with two structural-similarity thresholds (Tanimoto less than 0.80 or 0.70) computed against training-set products. The ‘Cryptic BGCs’ set was partitioned only by the four sequence cutoffs because reference products are absent. Model performance was reported per partition using metrics such as success rate, mean structural similarity, structure and scaffold recovery uniqueness (details in ‘Model evaluation metrics’). Data augmentation: to address the limited availability of curated BGC–SM pairs (3,029 cases) and improve the model’s ability to generalize in sparsely populated regions of chemical space, we implemented a tailored data augmentation procedure using RDKit in Python 21 (version 3.10, https://www.python.org/ ). Two complementary strategies were used: (1) Randomized SMILES augmentation: canonical SMILES strings were re-enumerated via the ‘MolToSmiles’ function by setting the ‘doRandom’ parameter as ‘True’, producing multiple valid SMILES representations with randomized atom order while retaining chemical identity. (2) Structural features-aligned SMILES augmentation: This strategy was designed to maintain the core biosynthetic semantics of the molecule while introducing expression-level diversity in its SMILES representation. The procedure consisted of the following steps (Supplementary Fig. 2):

(1) Scaffold extraction: the Bemis–Murcko chemical scaffold of each input SMILES string was obtained via the ‘GetScaffoldFor- Mol’ function. (2) Functional moiety mapping: scaffold atom indices were identified by the function ‘GetSubstructMatches’, ensuring that all atoms belonging to the scaffold (core ring systems and linkers) were preserved in both position and order. (3) Substituent re-enumeration: atoms outside the scaffold (substituents and side chains) were treated as molecular subgraphs and their atom indices were randomly renumbered starting from a random atom and topological path. This step introduced diversity in non-core atom ordering without altering the scaffold. (4) Graph reconstruction: the renumbered nonscaffold atom indices were combined with the fixed scaffold atom indices to form a reconstructed molecular graph of atomic numbers.

(5) SMILES generation: the final structural features-aligned SMILES string was obtained from the reconstructed molecular graph using the functions of ‘RenumberAtoms’ and ‘MolToSmiles’ with canonical=False, isomericSmiles=False, kekuleSmiles=True. The use of Kekulé SMILES representations removes aromaticity and stereochemical annotations, thereby reducing representational complexity for sequence-based modeling.

This process ensures scaffold-level structure, while permuting peripheral substituents to generate chemically equivalent yet syntactically diverse representations. For each molecule, up to 100 structurally aligned but atom order-diverse SMILES strings were generated, all sharing the same scaffold atom order. Using randomized SMILES enumeration, the training set was expanded to 173,570 augmented samples, whereas the features-aligned SMILES augmentation strategy produced 54,234 augmented instances. The latter configuration was selected for final model training owing to improved structural recovery and biosynthetic fidelity observed during validation.

Model development . Model training: we adopted a tenfold crossvalidation strategy for model training. The entire dataset was randomly partitioned into ten mutually exclusive, equal-sized subsets (folds). Model training was performed over ten iterations, with each itera - tion using nine folds for training and the remaining fold for validation. The transformer architecture consisted of six encoder layers and six decoder layers, each equipped with eight attention heads and an embedding dimension of 512, resulting in approximately 100 million trainable parameters (Supplementary Table 1). For each batch during training, both source and target sequences were first tokenized and embedded, and then passed through a positional encoding layer to retain the order information of the sequences. The encoder transformed the embedded source sequence into a context-rich representation, which was then consumed by the decoder, along with the embedded target sequence, to autoregressively predict the next token. Causal masks were applied to ensure that the decoder had no access to future target tokens. Decoder outputs were transformed through a linear layer followed by a softmax activation to generate token-level probability distributions. The predic - tions of the model were compared against the ground-truth target sequence using the cross-entropy loss. Model parameters were updated via backpropagation. Regularization was applied using dropout rate of 0.1. Optimization employed AdamW with a learning rate of 10 −4 and a batch size of 64; other transformer parameters followed default settings. Hyperparameters were tuned via grid search method (Supplementary Table 1). Model performance was monitored after each epoch on a held-out validation set and early stopping was triggered if no improvement was observed for ten consecutive epochs to avoid over-fitting issues. For each fold, the checkpoint achieving the best validation performance was retained. Final predictions were generated by aggregating outputs from the ten fold-specific models, enabling ensemble-based consensus scoring and improving robustness against partition-specific bias. DeepSeMS was implemented by PyTorch (version 2.1.0, https://pytorch. org/ ) in Python, and trained on up to eight GPUs of ‘NVIDIA RTX 4090’.

Model evaluation DeepSeMS was assessed using two independent test datasets: a ‘Known BGCs’ dataset designed to measure prediction accuracy on well-characterized BGCs and a ‘ Cryptic BGCs’ dataset aimed at evaluating the model’s generalization (see ‘External test datasets’). During model evaluation, a target mask was applied to the decoder to prevent it from attending to future positions in the target sequence. Given the encoded BGC-derived functional-domain features and the target mask, the model was initiated by the generation of a start-of-sequence token. At each step, the token with the highest predicted probability was selected and appended to the growing output sequence, which in turn served as input for subsequent token generation. The process terminated when an end-of-sequence token was produced. The final output sequence was decoded to SMILES strings of the predicted SM structure based on the predefined vocabulary of target tokens, followed by chemical validity checking and canonicalization using the functions of ‘MolToSmiles’ with canonical=True. To quantify the confidence of each prediction, we defined a prediction score based on the log-likelihood of the generated sequence (equation ( 1 ))

```text
Prediction score = ∑ log ( probabilities )
```

length penalty , (1)

( length of sequence )

where: ∑ log ( probabilities ) is the sum of the log-probabilities of all tokens selected during the sequence generation process, length of sequence is the length of the generated sequence (total number of generated tokens) and length penalty is a factor set to 0.6 in this study to adjust the score based on the length of the generated sequence, penalizing overly long outputs to balance the trade-off between sequence length and the cumulative probability. We additionally defined a consensus frequency metric to quantify the degree of agreement across independently trained models in predicting the same chemical structure, thereby reflecting the robustness and reproducibility of SM predictions. For each BGC, the top ten predicted SMILES strings were generated across the ensemble of fold-specific checkpoints. The consensus frequency corresponds to the number of models converging on an identical structure. Candidates were ranked primarily by consensus frequency and secondarily by prediction score, and the top-ranked structure was reported as the final prediction unless otherwise specified.

Model evaluation metrics . We implemented a suite of metrics for evaluating the performances of DeepSeMS model and benchmarking it against existing methods, using RDKit in Python. Chemical validity: the proportion of chemically valid SMILES strings successfully parsed by the ‘MolToSmiles’ function. Structural similarity: the Tanimoto coefficient between two structures, computed from Morgan fingerprints (radius = 2 bonds) via the functions of ‘TanimotoSimilarity’ and ‘GetMorganFingerprint’ 48 , 49 . Molecular scaffold: the core structure or framework of a molecule obtained by the function of ‘GetScaffoldForMol’ using Murcko-type decomposition. Molecular shape: the generic scaffold framework generated by the function of ‘MakeScaffoldGeneric’. Molecular properties: the molecular weight, heavy-atom count and quantitative estimate of QED, are calculated by the functions of ‘MolWt’, ‘HeavyAtomCount’ and ‘qed’, respectively. Chemical space: the distribution of Morgan fingerprints for all SM structures visualized by Matplotlib and Seaborn. Synthetic accessibility: the synthetic accessibility score estimated from molecular complexity and fragment contributions calculated by SAscorer 50 . Structural uniqueness: refers to the proportion of structurally distinct molecules among all valid predictions. Molecular NS: quantifies the degree of structural dissimilarity between each predicted molecule and all known compounds, thereby measuring the extent to which predictions venture into previously unexplored regions of chemical space. The molecular NS is calculated as defined in equation ( 2 ) (see ‘Large-scale SMs mining’).

Genome mining and analysis Global ocean BGCs dataset construction . We compiled a large-scale biosynthetic resource from 27,139 global ocean MAGs retrieved from the OMD 31 ( https://microbiomics.io/ocean/ ). BGCs were identified

following the same domain-based detection procedures applied to the ‘Cryptic BGCs’ set, yielding a comprehensive ‘global ocean BGCs’ dataset comprising 46,786 BGCs. This dataset provides the basis for large-scale mining of structurally and functionally diverse SMs beyond currently characterized reference compounds. Associated sample metadata, including geographic coordinates, oceanographic parameters and habitat classifications, were also obtained from OMD, enabling downstream analysis of the geographical distribution and ecological characteristics of the predicted SM repertoire.

Large-scale SMs mining . The large-scale mining of novel SMs from the global ocean BGCs, derived from the OMD dataset, was performed using the DeepSeMS model implemented in PyTorch. To estimate the structural novelty of the predicted SMs relative to known biosynthetic chemical space (MIBiG database), we introduced a molecular NS for each predicted SM as

## 1 − Max Similarity

0 . 8353 ) × 100 , (2)

## Molecular NS = (

where Max Similarity is the highest Tanimoto coefficient between the predicted SM and any known SM. The raw ( 1 − Max Similarity ) values were highly compressed (<0.84) across the dataset, limiting interpretability. The constant 0 . 8353 corresponds to the range (maximum–minimum) of pairwise similarities among all SMs in MIBiG database, enabling minimum–maximum normalization to a 0–100 scale. In this framework, a score of 0 denotes identity to a known compound, whereas 100 represents the structure with the lowest similarity observed in the reference space. Molecular scaffolds and genetic shapes were derived via Murcko-type decomposition using RDKit functions ‘GetScaffoldFor- Mol’ and ‘MakeScaffoldGeneric’. Geographical coverage, ocean diversities and ecological distribution characteristics of the global ocean SMs were analyzed according to the metadata from the OMD database 31 . ‘Diversity’ was defined as the percentage of unique SM structures within an ocean province. Elemental composition (O, N and C content) was calculated based on the molecular weight percentage of oxygen, nitrogen and carbon atoms, respectively. Ocean-wide distributions were visualized in R (version 4.1.2) using bathymetry data from the GEBCO 2025 Grid ( https://doi.org/10.5285/37c52e96-24ea-67ce-e063- 7086abc05f29 ) and coastline data from Natural Earth. To assess biomedical potential, we performed structure-based virtual screening of predicted SMs against scaffolds and functional groups associated with the following established antibiotic classes: (1) contain a substructure of 2-azetidinone in a bicyclic scaffold as β-lactams, (2) contain one or more aminosugars as aminoglycosides, (3) contain a scaffold of tetracene as tetracyclines, (4) contain a scaffold of 2-oxazolidon as oxazolidinones, (5) contain a substructure of dichloroacetamide as chloramphenicols, (6) contain a substructure of lactone in a macro ring with 14 or more atoms as macrolides, (7) contain a substructure of amide and aromatic moiety in a macro ring with 14 or more atoms as ansamycins and (8) contain a scaffold of 4-quinolone as quinolones. The virtual screening was also implemented using RDKit in Python by calculating whether the structures contain the above known antibiotic activity of functional groups. The SM structures in Fig. 4 were visualized and calculated for stereochemical information by ChemDraw (version 23.1.1).

Structure, scaffold and shape terminology . For each predicted and reference metabolite, the structure refers to the complete standardized molecular graph, including all atoms, bonds, stereochemistry and substituents, as represented by canonical SMILES after hydrogen normalization and tautomer canonicalization. The scaffold is defined following the Bemis–Murcko framework, in which each molecule is reduced to its ring systems and linkers, with all side chains removed 51 .

In this study, the term ‘shape’ denotes the two-dimensional connectivity and topology of the Bemis–Murcko scaffold, a usage consistent with prior cheminformatics literature 52 – 54 . This definition captures the atomic arrangement pattern of the scaffold in two dimensions, without implying three-dimensional conformation.

Web server implementation The DeepSeMS web server was built using Django (version 4.2.6, https:// www.djangoproject.com/ ) as the core framework, with SQLite (version 3.41.2, https://www.sqlite.org/ ) for data management, Python for backend applications and Docker (version 24.0.6) to ensure a portable and reproducible deployment environment. The frontend was developed by JavaScript, AJAX, JQuery and BootStrap (version 5.3.2, https://v5.bootcss.com/ ) for a responsive, user-friendly interface. We also applied RDKit in Python for chemical structure visualization, molecular properties calculation, known SMs comparison and antibiotic potential analysis.

Reporting summary Further information on research design is available in the Nature Portfolio Reporting Summary linked to this article.

Data availability All data used in this work were obtained from public data depositories and are specified in the methods section. The curated training dataset used for DeepSeMS is available via Figshare at https://doi.org/ 10.6084/m9.figshare.29680658 (ref. 55 ). Pretrained DeepSeMS model checkpoint files and the Pfam database (version 36.0) required for local execution are available via Zenodo at https://doi.org/10.5281/ zenodo.18217861 (ref. 56 ). The dataset of the global ocean SMs is provided both as part of the Source data file and through the DeepSeMS web server at https://biochemai.cstspace.cn/deepsems/downloads/ . Source data are provided with this paper.

Code availability The DeepSeMS web server and the integrated global ocean SMs resource are freely available with no login requirements at https:// biochemai.cstspace.cn/deepsems/ . The DeepSeMS source code and detailed tutorials for local installation and use are publicly available via Zenodo at https://doi.org/10.5281/zenodo.18217861 (ref. 56 ) and GitHub at: https://github.com/tjcadd2020/DeepSeMS and https:// github.com/lab-of-biochemai/DeepSeMS/ .

## References

1. Clardy, J. & Walsh, C. Lessons from natural molecules. Nature 432 , 829–837 (2004).

2. Xu, T. et al. NPBS Atlas: a comprehensive data resource for exploring the biological sources of natural products. J. Cheminform. 17 , 172 (2025).

3. Newman, D. J. & Cragg, G. M. Natural products as sources of new drugs over the nearly four decades from 01/1981 to 09/2019. J. Nat. Prod. 83 , 770–803 (2020).

4. Koehn, F. E. & Carter, G. T. The evolving role of natural products in drug discovery. Nat. Rev. Drug Discov. 4 , 206–220 (2005).

5. Vanni, C. et al. Unifying the known and unknown microbial coding sequence space. eLife 11 , e67667 (2022).

6. Wirbel, J., Bhatt, A. S. & Probst, A. J. The journey to understand previously unknown microbial genes. Nature 626 , 267–269 (2024).

7. Scherlach, K. & Hertweck, C. Mining and unearthing hidden biosynthetic potential. Nat. Commun. 12 , 3864 (2021).

8. Medema, M. H. et al. antiSMASH: rapid identification, annotation and analysis of secondary metabolite biosynthesis gene clusters in bacterial and fungal genome sequences. Nucleic Acids Res. 39 , W339–W346 (2011).

9. Skinnider, M. A. et al. Genomes to natural products PRediction Informatics for Secondary Metabolomes (PRISM). Nucleic Acids Res. 43 , 9645–9662 (2015).

10. Hannigan, G. D. et al. A deep learning genome-mining strategy for biosynthetic gene cluster prediction. Nucleic Acids Res. 47 , e110 (2019).

11. Skinnider, M. A. et al. Comprehensive prediction of secondary metabolite structure and biological activity from microbial genome sequences. Nat. Commun. 11 , 6058 (2020).

12. Blin, K. et al. antiSMASH 7.0: new and improved predictions for detection, regulation, chemical structures and visualisation. Nucleic Acids Res. 51 , W46–W50 (2023).

13. Chen, J. et al. Global marine microbial diversity and its potential in bioprospecting. Nature 633 , 371–379 (2024).

14. Cimermancic, P. et al. Insights into secondary metabolism from a global analysis of prokaryotic biosynthetic gene clusters. Cell 158 , 412–421 (2014).

15. Liu, M., Li, Y. & Li, H. Deep learning to predict the biosynthetic gene clusters in bacterial genomes. J. Mol. Biol. 434 , 167597 (2022).

16. Walsh C. T. & Tang Y. Natural Product Biosynthesis: Chemical Logic and Enzymatic Machinery Ch. 1 (Royal Society of Chemistry, 2017).

17. Bernhardt, R. Cytochromes P450 as versatile biocatalysts. J. Biotechnol. 124 , 128–145 (2006).

18. Vaswani, A. et al. Attention is all you need. Adv. Neural Inf. Process. Syst. 30 , 5998–6008 (2017).

19. Wolf, T. et al. Transformers: state-of-the-art natural language processing. In Proc. 2020 EMNLP (Systems Demonstrations) (eds Liu, Q. & Schlangen, D.) 38–45 (Association for Computational Linguistics, 2020).

20. Saldívar-González, F. I., Aldas-Bulos, V. D., Medina-Franco, J. L. & Plisson, F. Natural product drug discovery in the artificial intelligence era. Chem. Sci. 13 , 1526–1546 (2021).

21. Diao, Y. et al. Macrocyclization of linear molecules by deep learning to facilitate macrocyclic drug candidates discovery. Nat. Commun. 14 , 4552 (2023).

22. Terlouw, B. R. et al. MIBiG 3.0: a community-driven effort to annotate experimentally validated biosynthetic gene clusters. Nucleic Acids Res. 51 , D603–D610 (2023).

23. Outeiral, C. & Deane, C. M. Codon language embeddings provide strong signals for use in protein engineering. Nat. Mach. Intell. 6 , 170–179 (2024).

24. Weininger, D. SMILES, a chemical language and information system. J. Chem. Inf. Model. 28 , 31–36 (1988).

25. Polykovskiy, D. et al. Molecular Sets (MOSES): a benchmarking platform for molecular generation models. Front. Pharmacol. 11 , 565644 (2020).

26. Arús-Pous, J. et al. Randomized SMILES strings improve the quality of molecular generative models. J. Cheminform. 11 , 71 (2019).

27. Pascoalino, L. A. et al. in Natural Secondary Metabolites (eds Carocho, M. et al.) 437–474 (Springer, 2023).

28. Becerril, A. et al. Uncovering production of specialized metabolites by Streptomyces argillaceus : activation of cryptic biosynthesis gene clusters using nutritional and genetic approaches. PLoS ONE 13 , e0198145 (2018).

29. Zheng, X. et al. Biosynthesis of the pyrrolidine protein synthesis inhibitor anisomycin involves novel gene ensemble and cryptic biosynthetic steps. Proc. Natl Acad. Sci. USA 114 , 4135–4140 (2017).

30. Wills, T. J. & Lipkus, A. H. Structural approach to assessing the innovativeness of new drugs finds accelerating rate of innovation. ACS Med. Chem. Lett. 11 , 2114–2119 (2020).

31. Paoli, L. et al. Biosynthetic potential of the global ocean microbiome. Nature 607 , 111–118 (2022).

32. Wong, F. et al. Discovery of a structural class of antibiotics with explainable deep learning. Nature 626 , 177–185 (2024).

33. Sadeghi, A. et al. Diversity of the ectoines biosynthesis genes in the salt tolerant Streptomyces and evidence for inductive effect of ectoines on their accumulation. Microbiol. Res. 169 , 699–708 (2014).

34. Pastor, J. M. et al. Ectoines in cell stress protection: uses and biotechnological production. Biotechnol. Adv. 28 , 782–801 (2010).

35. Widderich, N. et al. Biochemical properties of ectoine hydroxylases from extremophiles and their wider taxonomic distribution among microorganisms. PLoS ONE 9 , e93809 (2014).

36. Dinglasan, J. L. N., Otani, H., Doering, D. T., Udwary, D. & Mouncey, N. J. Microbial secondary metabolites: advancements to accelerate discovery towards application. Nat. Rev. Microbiol. 23 , 338–354 (2025).

37. GBD 2021 Antimicrobial Resistance Collaborators Global burden of bacterial antimicrobial resistance 1990-2021: a systematic analysis with forecasts to 2050. Lancet 404 , 1199–1226 (2024).

38. Coelho et al. Towards the biogeography of prokaryotic genes. Nature 601 , 252–256 (2022).

39. Ma, B. et al. A genomic catalogue of soil microbiomes boosts mining of biodiversity and genetic resources. Nat. Commun. 14 , 7318 (2023).

40. Dai, R. et al. Crop root bacterial and viral genomes reveal unexplored species and microbiome patterns. Cell 188 , 2521–2539 (2025).

41. Elmassry, M. M. et al. A meta-analysis of the gut microbiome in inflammatory bowel disease patients identifies disease-associated small molecules. Cell Host Microbe 33 , 218–234 (2025).

42. Donia, M. S. et al. A systematic analysis of biosynthetic gene clusters in the human microbiome reveals a common family of antibiotics. Cell 158 , 1402–1414 (2014).

43. Madani, A. et al. Large language models generate functional protein sequences across diverse families. Nat. Biotechnol. 41 , 1099–1106 (2023).

44. Wang, Y. et al. Retrosynthesis prediction with an interpretable deep-learning framework based on molecular assembly tasks. Nat. Commun. 14 , 6155 (2023).

45. Mistry, J. et al. Pfam: the protein families database in 2021. Nucleic Acids Res. 49 , D412–D419 (2021).

46. Camacho, C. et al. BLAST+: architecture and applications. BMC Bioinformatics 10 , 421 (2009).

47. Acinas, S. G. et al. Deep ocean metagenomes provide insight into the metabolic architecture of bathypelagic microbial communities. Commun. Biol. 4 , 604 (2021).

48. Bajusz, D., Rácz, A. & Héberger, K. Why is Tanimoto index an appropriate choice for fingerprint-based similarity calculations?. J. Cheminform. 7 , 20 (2015).

49. Rogers, D. & Hahn, M. Extended-connectivity fingerprints. J. Cheminform. 50 , 742–754 (2010).

50. Ertl, P. & Schuffenhauer, A. Estimation of synthetic accessibility score of drug-like molecules based on molecular complexity and fragment contributions. J. Cheminform. 1 , 8 (2009).

51. Bemis, G. W. & Murcko, M. A. The properties of known drugs. 1. Molecular frameworks. J. Med. Chem. 39 , 2887–2893 (1996).

52. Schneider, G. & Fechner, U. Computer-based de novo design of drug-like molecules. Nat. Rev. Drug Discov. 4 , 649–663 (2005).

53. Rossen, L., Sirockin, F., Schneider, N. & Grisoni, F. Scaffold hopping with generative reinforcement learning. J. Chem. Inf. Model. 65 , 6513–6525 (2025).

54. Taylor, R. D., MacCoss, M. & Lawson, A. D. Rings in drugs. J. Med. Chem. 57 , 5845–5859 (2014).

55. Xu, T. et al. DeepSeMS: revealing hidden biosynthetic potential of the global ocean microbiome with a large language model. figshare https://doi.org/10.6084/ m9.figshare.29680658 (2025).

56. Xu, T. et al. Code (v1.0) for DeepSeMS: revealing hidden biosynthetic potential of the global ocean microbiome with a large language model. Zenodo https://doi.org/10.5281/ zenodo.18692427 (2025).

Acknowledgements This work was supported by the National Natural Science Foundation of China (grant nos. 92251307 to R.Z. and G. Zhang, 92451303 to P.Z., 32470098 to N.J. and 82170542 to R.Z.), the National Key Research and Development Program of China (grant no. 2023YFA0915501 to G. Zhang), the Shanghai Oriental Talents Program (grant no. BJJY2024098 to R.Z.), the Smart Grid-National Science and Technology Major Project (grant no. 2025ZD0807500 to T.X.) and the Informatization Plan of Chinese Academy of Sciences (grant no. CAS-WX2021SF-0307 to T.X.). We are grateful for the computational support from the Center for Scientific Computing and the Supercomputing Center of the School of Life Sciences and Technology, Tongji University. We also acknowledge the use of resources provided by Beijing PARATERA Tech Corp. Ltd. and China Science & Technology Cloud. The funders had no role in the study design, data collection and analysis, decision to publish, or preparation of the manuscript.

Author contributions N.J., R.Z., G. Zhao and G. Zhang conceived and designed the study. T.X. and Y.Y. drafted the manuscript. R.Z., W.L., J.L., Y.Z., P.Z., G. Zhang, G. Zhao and N.J. reviewed and edited the manuscript. All authors read and approved the final manuscript.

Competing interests The authors declare no competing interests.

Additional information Supplementary information The online version contains supplementary material available at https://doi.org/10.1038/s43588-026-00983-1 .

Correspondence and requests for materials should be addressed to Ruixin Zhu, Guoqing Zhang, Guoping Zhao or Na Jiao.

Peer review information Nature Computational Science thanks Ruibo Wu and the other, anonymous, reviewer(s) for their contribution to the peer review of this work. Primary Handling Editor: Kaitlin McCardle, in collaboration with the Nature Computational Science team.

Reprints and permissions information is available at www.nature.com/reprints .

Publisher’s note Springer Nature remains neutral with regard to jurisdictional claims in published maps and institutional affiliations.

Springer Nature or its licensor (e.g. a society or other partner) holds exclusive rights to this article under a publishing agreement with the author(s) or other rightsholder(s); author self-archiving of the accepted manuscript version of this article is solely governed by the terms of such publishing agreement and applicable law.

© The Author(s), under exclusive licence to Springer Nature America, Inc. 2026

1 Shanghai Key Laboratory of Maternal Fetal Medicine, Shanghai Institute of Maternal–Fetal Medicine and Gynecologic Oncology, Clinical and Translation Research Center, Shanghai First Maternity and Infant Hospital, School of Life Sciences and Technology, Tongji University, Shanghai, People’s Republic of China. 2 State Key Laboratory of Fluorine and Nitrogen Chemistry and Advanced Materials, Shanghai Institute of Organic Chemistry, Chinese Academy of Sciences, Shanghai, People’s Republic of China. 3 State Key Laboratory of Genetic and Development of Complex Phenotypes, Fudan Microbiome Center, School of Life Sciences, Fudan University, Shanghai, People’s Republic of China. 4 National Genomics Data Center and Bio-Med Big Data Center, CAS Key Laboratory of Computational Biology, Shanghai Institute of Nutrition and Health, University of Chinese Academy of Sciences, Shanghai, People’s Republic of China. 5 School of Life Science, Hangzhou Institute for Advanced Study, University of Chinese Academy of Sciences, Hangzhou, People’s Republic of China. 6 These authors contributed equally: Tingjun Xu, Yuwei Yang. e-mail: rxzhu@tongji.edu.cn ; gqzhang@picb.ac.cn ; gpzhao@sibs.ac.cn ; najiao@fudan.edu.cn
