export type CandidateStatus = "Shortlisted" | "Interview" | "Review" | "Rejected";

export interface ScoreBreakdown {
  skills: number;
  experience: number;
  education: number;
  certifications: number;
}

export interface Candidate {
  id: string;
  rank: number;
  name: string;
  email: string;
  phone: string;
  avatar: string;
  atsScore: number;
  matchPercentage: number;
  skillMatch: number;
  qualityScore: number;
  experience: number;
  skills: string[];
  missingSkills: string[];
  matchedSkills: string[];
  status: CandidateStatus;
  verdict: string;
  recommendation: string;
  education: string[];
  certifications: string[];
  company: string;
  resumeText: string;
  scoreBreakdown: ScoreBreakdown;
  reasoning: string[];
  interviewQuestions?: string[];
  filename?: string;
  growth?: number;
}

export interface JobDescription {
  id: string;
  title: string;
  department: string;
  requiredSkills: string[];
  experienceRequired: number;
  applicants: number;
  status: "Active" | "Closed" | "Draft";
  postedDate: string;
}

export interface DashboardStats {
  totalApplications: number;
  shortlisted: number;
  rejected: number;
  avgAtsScore: number;
  activeJobs: number;
  applicationsGrowth: number;
  shortlistedGrowth: number;
  rejectedGrowth: number;
  scoreGrowth: number;
}

export interface InterviewQuestion {
  id: string;
  category: "Technical" | "Behavioral" | "Domain Specific";
  question: string;
  candidateId: string;
}
