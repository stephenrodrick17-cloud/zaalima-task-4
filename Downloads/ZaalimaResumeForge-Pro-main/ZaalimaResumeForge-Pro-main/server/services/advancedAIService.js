const axios = require('axios');

const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY || process.env.OPENAI_API_KEY;
const OPENROUTER_API_URL = 'https://openrouter.ai/api/v1/chat/completions';

const groqRequest = async (messages, temperature = 0.7, maxTokens = 3000) => {
  if (!OPENROUTER_API_KEY) {
    throw new Error('API key not configured. Please set OPENROUTER_API_KEY in environment variables.');
  }

  try {
    const payload = {
      model: 'google/gemini-2.0-flash-001',
      messages,
      temperature,
      max_tokens: maxTokens,
    };

    const response = await axios.post(OPENROUTER_API_URL, payload, {
      headers: {
        'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
        'Content-Type': 'application/json',
      },
      timeout: 45000,
    });

    return response.data.choices[0]?.message?.content;
  } catch (error) {
    console.error('OpenRouter API error:', error.response?.data || error.message);
    throw new Error(error.response?.data?.error?.message || 'AI service unavailable');
  }
};

// 1. Brutal Honest Review
exports.brutalHonestReview = async (resumeText) => {
  const content = await groqRequest([
    {
      role: 'system',
      content: `You are a brutally honest senior hiring manager from FAANG companies (Google, Meta, Amazon, Apple, Microsoft).
You've reviewed 10,000+ resumes and rejected 95% of them. You have ZERO tolerance for mediocrity.

Analyze this resume with brutal honesty. Point out:
- Weak points that would get it rejected immediately
- Missing impact and quantifiable results
- Red flags (gaps, job hopping, vague descriptions, buzzwords without substance)
- Generic statements that add no value
- Poor formatting or ATS issues
- Lack of leadership, ownership, or business impact

Be direct, harsh but constructive. Tell them exactly why they won't get past the first screen.
Return valid JSON with this structure:
{
  "overallVerdict": "One brutal sentence summary",
  "rejectionReasons": ["reason 1", "reason 2", ...],
  "weakPoints": [
    {
      "section": "Experience/Skills/Summary/etc",
      "issue": "What's wrong",
      "impact": "Why it matters",
      "fix": "How to fix it"
    }
  ],
  "redFlags": ["flag 1", "flag 2", ...],
  "missingElements": ["element 1", "element 2", ...],
  "strengthsIfAny": ["strength 1", "strength 2", ...],
  "actionableSteps": [
    {
      "priority": "Critical/High/Medium",
      "action": "Specific action to take",
      "why": "Why this matters"
    }
  ],
  "honestScore": {
    "current": 0-100,
    "potential": 0-100,
    "gap": "What's holding them back"
  }
}`
    },
    {
      role: 'user',
      content: `Give me a brutally honest review of this resume. Don't hold back. Tell me exactly why I'd get rejected.\n\nResume:\n${resumeText}`
    }
  ], 0.8, 3500);

  try {
    return JSON.parse(content);
  } catch (error) {
    console.error('JSON parse error:', error);
    return {
      overallVerdict: "Unable to parse review",
      rejectionReasons: [],
      weakPoints: [],
      redFlags: [],
      missingElements: [],
      strengthsIfAny: [],
      actionableSteps: [],
      honestScore: { current: 0, potential: 0, gap: "Parse error" }
    };
  }
};

// 2. ATS Optimizer
exports.atsOptimizer = async (resumeText, jobDescription) => {
  const content = await groqRequest([
    {
      role: 'system',
      content: `You are an expert ATS (Applicant Tracking System) optimization specialist.
You understand exactly how ATS systems parse, score, and rank resumes.

Analyze the resume against the job description and provide:
- Exact ATS compatibility score (0-100)
- Missing critical keywords from the JD
- Found keywords and their frequency
- Keyword density heatmap data
- Rewritten bullet points optimized for ATS
- Section-by-section optimization suggestions

Return valid JSON with this structure:
{
  "atsScore": 0-100,
  "compatibility": "Excellent/Good/Fair/Poor",
  "missingKeywords": [
    {
      "keyword": "keyword",
      "importance": "Critical/High/Medium",
      "whereToAdd": "Which section",
      "context": "How to naturally include it"
    }
  ],
  "foundKeywords": [
    {
      "keyword": "keyword",
      "frequency": number,
      "locations": ["section1", "section2"]
    }
  ],
  "keywordHeatmap": {
    "technical": { "found": number, "total": number, "percentage": number },
    "soft": { "found": number, "total": number, "percentage": number },
    "industry": { "found": number, "total": number, "percentage": number },
    "tools": { "found": number, "total": number, "percentage": number }
  },
  "optimizedBullets": [
    {
      "original": "original bullet",
      "optimized": "ATS-optimized version",
      "keywordsAdded": ["keyword1", "keyword2"],
      "improvement": "Why this is better"
    }
  ],
  "sectionScores": {
    "summary": { "score": 0-100, "issues": [], "suggestions": [] },
    "experience": { "score": 0-100, "issues": [], "suggestions": [] },
    "skills": { "score": 0-100, "issues": [], "suggestions": [] },
    "education": { "score": 0-100, "issues": [], "suggestions": [] }
  },
  "formatIssues": ["issue1", "issue2"],
  "quickWins": ["quick fix 1", "quick fix 2"]
}`
    },
    {
      role: 'user',
      content: `Optimize this resume for ATS against this job description. Provide detailed keyword analysis and rewritten bullets.\n\nResume:\n${resumeText}\n\nJob Description:\n${jobDescription}`
    }
  ], 0.7, 4000);

  try {
    return JSON.parse(content);
  } catch (error) {
    console.error('JSON parse error:', error);
    return {
      atsScore: 0,
      compatibility: "Unknown",
      missingKeywords: [],
      foundKeywords: [],
      keywordHeatmap: {},
      optimizedBullets: [],
      sectionScores: {},
      formatIssues: [],
      quickWins: []
    };
  }
};

// 3. Bullet Point Transformer
exports.bulletPointTransformer = async (bullets, jobContext = '') => {
  const content = await groqRequest([
    {
      role: 'system',
      content: `You are an expert resume writer specializing in the XYZ formula:
"Accomplished [X] as measured by [Y] by doing [Z]"

Transform every bullet point into this format:
- Strong action verb
- Clear task/responsibility
- Quantifiable result/impact

If metrics are missing, ask intelligent questions to extract them.
Return valid JSON with this structure:
{
  "transformedBullets": [
    {
      "original": "original bullet",
      "transformed": "XYZ formula version",
      "actionVerb": "verb used",
      "task": "what was done",
      "metric": "measurable result",
      "impact": "business impact",
      "missingInfo": ["question1", "question2"] or null,
      "improvementScore": 0-100
    }
  ],
  "overallImprovement": "summary of changes",
  "metricsNeeded": [
    {
      "bullet": "which bullet",
      "questions": ["What was the team size?", "What was the timeline?", "What was the impact?"]
    }
  ]
}`
    },
    {
      role: 'user',
      content: `Transform these bullet points using the XYZ formula (Action + Task + Measurable Result). If metrics are missing, ask smart questions.\n\n${jobContext ? `Job Context: ${jobContext}\n\n` : ''}Bullets:\n${bullets.map((b, i) => `${i + 1}. ${b}`).join('\n')}`
    }
  ], 0.7, 3500);

  try {
    return JSON.parse(content);
  } catch (error) {
    console.error('JSON parse error:', error);
    return {
      transformedBullets: [],
      overallImprovement: "Parse error",
      metricsNeeded: []
    };
  }
};

// 4. Industry Tone Match
exports.industryToneMatch = async (resumeText, targetCompanies, targetRole) => {
  const companyList = Array.isArray(targetCompanies) ? targetCompanies.join(', ') : targetCompanies;

  const content = await groqRequest([
    {
      role: 'system',
      content: `You are an expert in corporate culture and industry-specific resume writing.
You understand the exact tone, language, and style that different companies look for:

- FAANG (Google, Meta, Amazon, Apple, Microsoft): Data-driven, impact-focused, scale-oriented, innovation
- Consulting (McKinsey, BCG, Bain, Deloitte): Strategic thinking, client impact, problem-solving
- Finance (Goldman Sachs, JP Morgan, BlackRock): Quantitative results, risk management, revenue impact
- Startups (YC companies, unicorns): Scrappy, ownership, 0-to-1 building, fast-paced
- Enterprise (IBM, Oracle, SAP): Process-oriented, stakeholder management, enterprise-scale

Rewrite the resume to match the target company culture and role.
Return valid JSON with this structure:
{
  "rewrittenSummary": "Industry-matched professional summary",
  "rewrittenExperience": [
    {
      "original": "original description",
      "rewritten": "industry-matched version",
      "toneChanges": "what changed and why",
      "keyPhrases": ["phrase1", "phrase2"]
    }
  ],
  "rewrittenSkills": {
    "technical": ["skill1", "skill2"],
    "soft": ["skill1", "skill2"],
    "industrySpecific": ["skill1", "skill2"]
  },
  "languageAdjustments": [
    {
      "from": "generic phrase",
      "to": "industry-specific phrase",
      "reason": "why this matters"
    }
  ],
  "cultureFit": {
    "score": 0-100,
    "strengths": ["strength1", "strength2"],
    "gaps": ["gap1", "gap2"]
  },
  "toneAnalysis": {
    "before": "description of original tone",
    "after": "description of new tone",
    "keyDifferences": ["diff1", "diff2"]
  }
}`
    },
    {
      role: 'user',
      content: `Rewrite this resume to match the tone and culture of ${companyList} for a ${targetRole} role. Make it sound elite and role-specific.\n\nResume:\n${resumeText}`
    }
  ], 0.7, 4000);

  try {
    return JSON.parse(content);
  } catch (error) {
    console.error('JSON parse error:', error);
    return {
      rewrittenSummary: "",
      rewrittenExperience: [],
      rewrittenSkills: {},
      languageAdjustments: [],
      cultureFit: {},
      toneAnalysis: {}
    };
  }
};

// 5. Final Polish Review
exports.finalPolishReview = async (resumeText) => {
  const content = await groqRequest([
    {
      role: 'system',
      content: `You are a meticulous resume editor and premium copywriter.
Scan the entire resume for:
- Weak words (helped, worked on, responsible for, etc.)
- Clichés and buzzwords (team player, hard worker, detail-oriented)
- Tense inconsistencies
- Generic lines that add no value
- Passive voice
- Redundancy
- Grammar and punctuation issues

Rewrite everything into sharp, premium, executive-level language.
Return valid JSON with this structure:
{
  "polishedResume": "Complete rewritten resume text",
  "changes": [
    {
      "section": "section name",
      "original": "original text",
      "polished": "improved text",
      "reason": "why this is better",
      "category": "weak-word/cliche/tense/generic/passive/grammar"
    }
  ],
  "weakWords": [
    {
      "word": "weak word",
      "count": number,
      "replacements": ["strong alternative 1", "strong alternative 2"]
    }
  ],
  "cliches": [
    {
      "phrase": "cliche phrase",
      "replacement": "premium alternative",
      "context": "where it appeared"
    }
  ],
  "tenseIssues": [
    {
      "issue": "description of tense problem",
      "fix": "how to fix it"
    }
  ],
  "genericLines": [
    {
      "line": "generic line",
      "why": "why it's generic",
      "replacement": "specific alternative"
    }
  ],
  "qualityScore": {
    "before": 0-100,
    "after": 0-100,
    "improvement": number
  },
  "readabilityScore": {
    "before": 0-100,
    "after": 0-100
  },
  "premiumLevel": "Entry/Mid/Senior/Executive"
}`
    },
    {
      role: 'user',
      content: `Polish this resume to premium executive-level language. Remove all weak words, clichés, and generic statements. Make it sharp and impactful.\n\nResume:\n${resumeText}`
    }
  ], 0.7, 4000);

  try {
    return JSON.parse(content);
  } catch (error) {
    console.error('JSON parse error:', error);
    return {
      polishedResume: "",
      changes: [],
      weakWords: [],
      cliches: [],
      tenseIssues: [],
      genericLines: [],
      qualityScore: {},
      readabilityScore: {},
      premiumLevel: "Unknown"
    };
  }
};

// 6. Dynamic Resume Strength Analysis
exports.analyzeResumeStrength = async (resumeData, jobDescription = '') => {
  const resumeText = `
Name: ${resumeData.personalInfo?.fullName || 'Not provided'}
Email: ${resumeData.personalInfo?.email || 'Not provided'}
Phone: ${resumeData.personalInfo?.phone || 'Not provided'}
Location: ${resumeData.personalInfo?.location || 'Not provided'}
Summary: ${resumeData.personalInfo?.summary || 'Not provided'}

EXPERIENCE:
${resumeData.experience?.map(exp => `
${exp.position} at ${exp.company} (${exp.startDate} - ${exp.endDate})
${exp.description}
`).join('\n') || 'No experience listed'}

EDUCATION:
${resumeData.education?.map(edu => `
${edu.degree} ${edu.field ? `in ${edu.field}` : ''} from ${edu.institution} (${edu.startDate} - ${edu.endDate})
`).join('\n') || 'No education listed'}

SKILLS:
${resumeData.skills?.map(s => s.name).join(', ') || 'No skills listed'}

PROJECTS:
${resumeData.projects?.map(proj => `
${proj.name}: ${proj.description}
Technologies: ${Array.isArray(proj.technologies) ? proj.technologies.join(', ') : proj.technologies || ''}
`).join('\n') || 'No projects listed'}
  `.trim();

  const prompt = jobDescription
    ? `Analyze this resume against the job description and provide a detailed strength score.

JOB DESCRIPTION:
${jobDescription}

RESUME:
${resumeText}`
    : `Analyze this resume and provide a detailed strength score.

RESUME:
${resumeText}`;

  const content = await groqRequest([
    {
      role: 'system',
      content: `You are an expert ATS (Applicant Tracking System) and resume analyzer. Analyze the resume and provide a comprehensive strength assessment.

Return ONLY valid JSON with this exact structure:
{
  "overallScore": <number 0-100>,
  "level": "<Excellent|Good|Fair|Needs Work>",
  "breakdown": {
    "personalInfo": <number 0-100>,
    "experience": <number 0-100>,
    "education": <number 0-100>,
    "skills": <number 0-100>,
    "projects": <number 0-100>,
    "atsCompatibility": <number 0-100>
  },
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "weaknesses": ["<weakness 1>", "<weakness 2>", "<weakness 3>"],
  "suggestions": [
    {
      "icon": "<emoji>",
      "text": "<suggestion text>",
      "priority": "<Critical|High|Medium|Low>",
      "section": "<personal|experience|education|skills|projects>"
    }
  ],
  "keywordMatch": {
    "matched": ["<keyword 1>", "<keyword 2>"],
    "missing": ["<keyword 1>", "<keyword 2>"],
    "coverage": <number 0-100>
  },
  "impactScore": <number 0-100>,
  "readabilityScore": <number 0-100>
}

Scoring criteria:
- Personal Info: Complete contact info, professional summary with impact
- Experience: Quantifiable achievements, action verbs, business impact
- Education: Relevant degrees, GPA if strong, certifications
- Skills: Technical depth, relevant to role, organized by category
- Projects: Real-world impact, technologies used, measurable results
- ATS Compatibility: Keywords, formatting, structure, no graphics/tables

Be strict but fair. Most resumes score 50-75. Only exceptional resumes score 85+.`
    },
    {
      role: 'user',
      content: prompt
    }
  ], 0.3, 2000);

  try {
    const jsonMatch = content.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      throw new Error('No JSON found in response');
    }
    return JSON.parse(jsonMatch[0]);
  } catch (parseError) {
    console.error('Failed to parse resume strength response:', content);
    throw new Error('Failed to analyze resume strength');
  }
};

module.exports = exports;
