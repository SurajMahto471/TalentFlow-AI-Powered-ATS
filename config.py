"""Application configuration, scoring weights, and skill taxonomy."""

from pathlib import Path

# Database
DB_PATH = Path(__file__).parent / "ats_database.db"

# ATS scoring weights (must sum to 1.0)
SKILL_WEIGHT = 0.50
EXPERIENCE_WEIGHT = 0.20
EDUCATION_WEIGHT = 0.15
CERTIFICATION_WEIGHT = 0.15

# Duplicate detection threshold
DUPLICATE_SIMILARITY_THRESHOLD = 0.85

# Known skills for extraction and matching
SKILL_TAXONOMY: list[str] = [
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "kotlin", "swift",
    "sql", "mysql", "postgresql", "mongodb", "redis", "oracle", "sqlite",
    "html", "css", "react", "angular", "vue", "nodejs", "django", "flask", "fastapi", "spring boot",
    "machine learning", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch", "scikit-learn",
    "pandas", "numpy", "matplotlib", "plotly", "power bi", "tableau",
    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "terraform", "ansible",
    "git", "github", "gitlab", "ci/cd", "agile", "scrum",
    "rest api", "graphql", "microservices", "linux", "bash",
    "data analysis", "data engineering", "etl", "spark", "hadoop", "kafka",
    "selenium", "pytest", "junit", "unit testing",
]

# Certification keywords
CERTIFICATION_KEYWORDS: list[str] = [
    "aws certified", "azure certified", "gcp certified", "google cloud certified",
    "pmp", "scrum master", "csm", "cissp", "comptia", "cisco ccna",
    "oracle certified", "microsoft certified", "mcsa", "mcse",
    "cka", "ckad", "terraform associate", "security+",
]

# Degree patterns for education detection
DEGREE_PATTERNS: list[str] = [
    r"b\.?\s*tech", r"b\.?\s*e\.?", r"bachelor", r"b\.?\s*sc", r"bca", r"bba",
    r"m\.?\s*tech", r"m\.?\s*e\.?", r"master", r"m\.?\s*sc", r"mca", r"mba", r"ph\.?\s*d",
    r"diploma", r"associate degree",
]

# Interview question bank keyed by skill
INTERVIEW_QUESTIONS: dict[str, list[str]] = {
    "python": [
        "Explain the difference between lists and tuples in Python.",
        "What are decorators and how do you use them?",
        "Explain list comprehensions with an example.",
    ],
    "java": [
        "Explain the difference between abstract classes and interfaces.",
        "What is the JVM and how does garbage collection work?",
        "Explain the concept of polymorphism in Java.",
    ],
    "sql": [
        "What is the difference between INNER JOIN and LEFT JOIN?",
        "Explain indexing and when it improves query performance.",
        "What is the difference between WHERE and HAVING clauses?",
    ],
    "machine learning": [
        "What is overfitting and how do you prevent it?",
        "Explain the bias-variance tradeoff.",
        "What is the difference between supervised and unsupervised learning?",
    ],
    "docker": [
        "What is the difference between a Docker image and a container?",
        "Explain Docker Compose and its use cases.",
        "How do you optimize Docker image size?",
    ],
    "aws": [
        "Explain the difference between S3, EBS, and EFS.",
        "What is an Auto Scaling Group and when would you use it?",
        "Describe the AWS shared responsibility model.",
    ],
    "react": [
        "Explain the React component lifecycle.",
        "What is the difference between state and props?",
        "What are React hooks and why were they introduced?",
    ],
    "django": [
        "Explain Django's MVT architecture.",
        "What are Django migrations and why are they important?",
        "How does Django ORM work?",
    ],
    "flask": [
        "What is a Flask blueprint?",
        "Explain request context vs application context.",
        "How do you handle authentication in Flask?",
    ],
    "kubernetes": [
        "What is the difference between a Pod and a Deployment?",
        "Explain Kubernetes Services and their types.",
        "What is a ConfigMap and when would you use it?",
    ],
}

DEFAULT_INTERVIEW_QUESTIONS: list[str] = [
    "Tell me about a challenging project you worked on.",
    "How do you prioritize tasks when handling multiple deadlines?",
    "Describe a time you had to learn a new technology quickly.",
]
