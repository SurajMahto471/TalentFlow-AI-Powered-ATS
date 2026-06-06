export const SAMPLE_JOB_DESCRIPTION = `Python Developer

Required Skills:
Python, SQL, Django, Docker, REST API

Experience: 3+ Years

Education: Bachelor's degree in Computer Science or related field

Certifications: AWS or cloud certification is a plus

Responsibilities:
- Build scalable backend services using Python and Django
- Design and optimize SQL databases
- Deploy applications using Docker and CI/CD pipelines`;

export const SAMPLE_CANDIDATES_CSV = `name,email,phone,skills,experience,education,certifications,company,resume_text
Rahul Kumar,rahul.kumar@email.com,9876543210,"Python, SQL, Django, Docker, REST API, Git",4,B.Tech Computer Science IIT Delhi,AWS Certified Developer,TechNova Solutions,"Built Django REST APIs serving 50k users. Deployed microservices with Docker."
Priya Sharma,priya.sharma@email.com,9123456780,"Python, SQL, Flask, Machine Learning, Pandas",2,M.Tech Data Science NIT Trichy,,DataPulse Analytics,"Developed ML pipelines and Flask APIs for data products."
Aman Singh,aman.singh@email.com,9988776655,"Java, Spring Boot, SQL, Microservices",5,B.E Information Technology,Oracle Certified Java Programmer,InfoCore Ltd,"5 years Java backend development with microservices architecture."
Sneha Patel,sneha.patel@email.com,9012345678,"Python, SQL, Docker, Kubernetes, AWS",3,B.Tech IT VIT Vellore,AWS Cloud Practitioner,CloudBridge Tech,"DevOps-focused Python developer with AWS and Kubernetes experience."
Vikram Rao,vikram.rao@email.com,8899776655,"HTML, CSS, JavaScript, React",1,BCA Bangalore University,,WebStart Studio,"Frontend developer with React portfolio projects."`;

export function createSampleCsvFile(): File {
  return new File([SAMPLE_CANDIDATES_CSV], "sample_candidates.csv", { type: "text/csv" });
}
