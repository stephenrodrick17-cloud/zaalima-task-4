const axios = require('axios');

const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY || process.env.OPENAI_API_KEY;
const OPENROUTER_API_URL = 'https://openrouter.ai/api/v1/chat/completions';

const groqRequest = async (messages, temperature = 0.7, maxTokens = 2000) => {
  if (!OPENROUTER_API_KEY) {
    console.error('No API key found. OPENROUTER_API_KEY:', process.env.OPENROUTER_API_KEY);
    throw new Error('API key not configured. Please set OPENROUTER_API_KEY in environment variables.');
  }

  try {
    const payload = {
      model: 'google/gemini-2.0-flash-001',
      messages,
      temperature,
      max_tokens: maxTokens,
    };
    console.log('Sending to Groq API:', JSON.stringify(payload, null, 2));

    const response = await axios.post(OPENROUTER_API_URL, payload, {
      headers: {
        'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    });

    return response.data.choices[0]?.message?.content;
  } catch (error) {
    console.error('OpenRouter API error:', error.response?.data || error.message);
    throw new Error(error.response?.data?.error?.message || 'AI service unavailable');
  }
};

// Analyze Job Description
exports.analyzeJD = async (jdText) => {
  const content = await groqRequest([
    {
      role: 'system',
      content: 'You are an expert ATS analyzer. Extract key skills and keywords from job descriptions. Return valid JSON only.'
    },
    {
      role: 'user',
      content: `Analyze this job description and extract key skills and keywords. Return as JSON: { "keywords": [], "priority": [], "skills": { "required": [], "preferred": [] }, "experience": "", "education": "" }. JD: ${jdText}`
    }
  ], 0.3);
  
  try {
    return JSON.parse(content);
  } catch {
    return { keywords: [], priority: [], skills: { required: [], preferred: [] } };
  }
};

// Rewrite Bullet Point
exports.rewriteBullet = async (bullet, keyword) => {
  return await groqRequest([
    {
      role: 'system',
      content: 'You are an expert resume writer. Rewrite bullet points to be impactful, ATS-optimized, and results-driven. Use the XYZ formula (Accomplished X, as measured by Y, by doing Z).'
    },
    {
      role: 'user',
      content: `Rewrite this resume bullet point to be impactful, include the keyword '${keyword}', and optimize for ATS. Use strong action verbs and quantify where possible. Bullet: ${bullet}`
    }
  ]);
};

// Calculate ATS Score
exports.calculateATSScore = async (resumeText, jdText) => {
  const content = await groqRequest([
    {
      role: 'system',
      content: 'You are an expert ATS scoring system. Compare resumes against job descriptions with strict analysis. Return valid JSON only.'
    },
    {
      role: 'user',
      content: `Compare this resume against the job description thoroughly. Return JSON: { "score": number, "missingKeywords": [], "foundKeywords": [], "suggestions": [], "sectionScores": { "skills": number, "experience": number, "education": number, "keywords": number }, "strengths": [], "weaknesses": [] }. Resume: ${resumeText} JD: ${jdText}`
    }
  ], 0.3);

  try {
    return JSON.parse(content);
  } catch {
    return { score: 0, missingKeywords: [], foundKeywords: [], suggestions: [] };
  }
};

// Generate Cover Letter
exports.generateCoverLetter = async (resumeText, jdText, tone = 'professional') => {
  return await groqRequest([
    {
      role: 'system',
      content: `You are an expert cover letter writer. Generate a compelling ${tone} cover letter. Be tailored to the role, highlight relevant experience, show enthusiasm. 3-4 paragraphs.`
    },
    {
      role: 'user',
      content: `Generate a ${tone} cover letter based on this resume and job description.\n\nResume: ${resumeText}\n\nJob Description: ${jdText}`
    }
  ], 0.7, 1500);
};

// Chat with AI Assistant
exports.chat = async (message, chatHistory = [], resumeContext = '') => {
  const systemMessage = `You are ResumeForge AI Assistant, an expert career advisor and resume writing assistant. You help users with:
- Resume writing tips and best practices
- ATS optimization advice
- Interview preparation tips
- Career guidance and job search strategies
- Cover letter writing advice
- Skill development recommendations
- Salary negotiation tips
- Professional branding guidance

Be concise, actionable, and friendly. If asked about something unrelated to careers/resumes, politely redirect.${resumeContext ? '\n\n' + resumeContext : ''}`;

  const messages = [
    { role: 'system', content: systemMessage },
    ...chatHistory.slice(-10),
    { role: 'user', content: message }
  ];

  return await groqRequest(messages, 0.7, 1000);
};

// Generate Dynamic Template Content
exports.generateTemplateContent = async (templateStyle, jobRole = 'Senior Professional', industry = 'Technology') => {
  const content = await groqRequest([
    {
      role: 'system',
      content: `You are a professional resume writer. Generate realistic, ATS-friendly resume content.
Return valid JSON with this exact structure:
{
  "personalInfo": { "name": "", "title": "", "email": "", "phone": "", "location": "", "linkedin": "", "website": "" },
  "summary": "2-3 sentence professional summary",
  "experience": [{ "company": "", "title": "", "startDate": "", "endDate": "", "location": "", "achievements": [] }],
  "skills": { "technical": [], "soft": [] },
  "education": [{ "school": "", "degree": "", "field": "", "year": "" }],
  "projects": [{ "name": "", "description": "", "tech": [], "link": "" }],
  "achievements": []
}`
    },
    {
      role: 'user',
      content: `Generate a complete resume for a ${jobRole} in the ${industry} industry using the ${templateStyle} template style. Make it realistic with quantified achievements.`
    }
  ], 0.7, 2500);

  try {
    return JSON.parse(content);
  } catch {
    return null;
  }
};

// Generate Interview Questions
exports.generateInterviewQuestions = async (jobTitle, company = '', jobDescription = '') => {
  const content = await groqRequest([
    {
      role: 'system',
      content: 'You are an expert interview coach. Generate relevant interview questions with suggested answer frameworks. Return valid JSON.'
    },
    {
      role: 'user',
      content: `Generate 8 interview questions for a ${jobTitle} position${company ? ` at ${company}` : ''}. Include behavioral, technical, and situational questions. Return JSON: { "questions": [{ "question": "", "type": "behavioral|technical|situational", "tip": "brief answer tip" }] }${jobDescription ? `. Job Description: ${jobDescription}` : ''}`
    }
  ], 0.7, 1500);

  try {
    return JSON.parse(content);
  } catch {
    return { questions: [] };
  }
};