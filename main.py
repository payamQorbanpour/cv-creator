#!/usr/bin/env python3
"""
CV Creator - Generate customized resumes and cover letters
"""
import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import argparse
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class CVCreator:
    def __init__(self, base_data_file="inputs/base_data.json", use_ai=False):
        self.base_data_file = base_data_file
        self.base_data = self.load_base_data()
        self.template_env = Environment(loader=FileSystemLoader('templates'))
        self.openai_client = None
        
        # Initialize AI if API key is available and use_ai is True
        api_key = os.getenv('OPENAI_API_KEY')
        if use_ai and api_key:
            try:
                self.openai_client = OpenAI(api_key=api_key)
                self.use_ai = True
                print("✓ AI features enabled (OpenAI API)")
            except Exception as e:
                print(f"⚠️  Failed to initialize OpenAI client: {e}")
                self.use_ai = False
        else:
            self.use_ai = False
            if use_ai and not api_key:
                print("⚠️  OPENAI_API_KEY not found - AI features disabled")
                print("   Set OPENAI_API_KEY in .env file to enable AI optimization")
        
    def load_base_data(self):
        """Load base personal data from JSON file"""
        if os.path.exists(self.base_data_file):
            with open(self.base_data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Create default template if not exists
            default_data = {
                "personal_info": {
                    "name": "Your Name",
                    "title": "Your Professional Title",
                    "email": "your.email@example.com",
                    "phone": "+1-234-567-8900",
                    "location": "City, Country",
                    "linkedin": "linkedin.com/in/yourprofile",
                    "github": "github.com/yourusername",
                    "website": "yourwebsite.com"
                },
                "summary": "Professional summary or objective statement",
                "experience": [
                    {
                        "title": "Job Title",
                        "company": "Company Name",
                        "location": "City, Country",
                        "start_date": "Jan 2020",
                        "end_date": "Present",
                        "responsibilities": [
                            "Key achievement or responsibility 1",
                            "Key achievement or responsibility 2",
                            "Key achievement or responsibility 3"
                        ]
                    }
                ],
                "education": [
                    {
                        "degree": "Degree Name",
                        "institution": "University Name",
                        "location": "City, Country",
                        "graduation_date": "Year",
                        "gpa": "3.8/4.0",
                        "honors": "Cum Laude"
                    }
                ],
                "skills": {
                    "Technical": ["Skill 1", "Skill 2", "Skill 3"],
                    "Languages": ["English (Native)", "Spanish (Fluent)"],
                    "Tools": ["Tool 1", "Tool 2", "Tool 3"]
                },
                "projects": [
                    {
                        "name": "Project Name",
                        "description": "Brief project description",
                        "technologies": ["Tech 1", "Tech 2"],
                        "link": "github.com/project"
                    }
                ],
                "certifications": [
                    {
                        "name": "Certification Name",
                        "issuer": "Issuing Organization",
                        "date": "Year"
                    }
                ]
            }
            with open(self.base_data_file, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, indent=4)
            return default_data
    
    def save_base_data(self):
        """Save modified base data"""
        with open(self.base_data_file, 'w', encoding='utf-8') as f:
            json.dump(self.base_data, f, indent=4)
    
    def parse_job_description_with_ai(self, text):
        """Parse plain text job description using AI (or basic parsing if AI unavailable)"""
        if not self.use_ai or not self.openai_client:
            # Basic parsing without AI
            lines = text.strip().split('\n')
            title = lines[0][:100] if lines else "Position"
            return {
                "title": title,
                "description": text,
                "requirements": [line.strip() for line in lines if line.strip() and len(line) > 20][:10]
            }
        
        prompt = f"""Parse this job description and extract structured information.
Return a JSON object with these fields:
- title: The job title
- description: A concise summary of the role (2-3 sentences)
- requirements: Array of key requirements and qualifications
- key_responsibilities: Array of main responsibilities
- desired_skills: Array of important skills mentioned
- company_name: Company name if mentioned, otherwise null

Job Description:
{text}

Return ONLY valid JSON, no markdown formatting."""

        try:
            print("  🤖 Parsing job description with AI...")
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert at parsing job descriptions and extracting structured information. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            result = response.choices[0].message.content.strip()
            # Remove markdown code blocks if present
            if result.startswith('```'):
                result = result.split('```')[1]
                if result.startswith('json'):
                    result = result[4:]
                result = result.strip()
            
            parsed = json.loads(result)
            print("  ✓ Job description parsed successfully")
            return parsed
            
        except Exception as e:
            print(f"  ⚠️  AI parsing failed: {e}")
            return {
                "title": "Position",
                "description": text[:500],
                "requirements": []
            }
    
    def parse_company_info_with_ai(self, text):
        """Parse plain text company information using AI (or basic parsing if AI unavailable)"""
        if not self.use_ai or not self.openai_client:
            # Basic parsing without AI - try to extract company name from first line
            lines = text.strip().split('\n')
            first_line = lines[0] if lines else "Company"
            # Try to extract company name (remove common prefixes)
            company_name = first_line.replace('About ', '').replace('Company: ', '').strip()[:100]
            return {
                "name": company_name,
                "about": text
            }
        
        prompt = f"""Parse this company information and extract structured details.
Return a JSON object with these fields:
- name: The ACTUAL company name mentioned in the text (e.g., "Tech Innovations Inc.", "Google", "Microsoft"). Do NOT use generic terms like "Company" or "The Company".
- about: Brief company description (2-3 sentences)
- industry: Industry/sector
- size: Company size if mentioned
- location: Location/headquarters if mentioned
- website: Website URL if mentioned
- values: Array of company values or culture points
- recent_news: Any recent achievements or news mentioned

Company Information:
{text}

IMPORTANT: Extract the EXACT company name from the text. If the company name appears anywhere (e.g., "About [Company Name]" or "[Company Name] is..."), use that exact name.
Return ONLY valid JSON, no markdown formatting."""

        try:
            print("  🤖 Parsing company information with AI...")
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert at parsing company information and extracting structured details. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            result = response.choices[0].message.content.strip()
            # Remove markdown code blocks if present
            if result.startswith('```'):
                result = result.split('```')[1]
                if result.startswith('json'):
                    result = result[4:]
                result = result.strip()
            
            parsed = json.loads(result)
            print("  ✓ Company information parsed successfully")
            return parsed
            
        except Exception as e:
            print(f"  ⚠️  AI parsing failed: {e}")
            return {
                "name": "Company",
                "about": text[:500]
            }
    
    def optimize_resume_bullets_with_ai(self, bullets, job_description):
        """Use AI to optimize resume bullets to match job description while keeping them human"""
        if not self.use_ai or not self.openai_client:
            return bullets
        
        bullets_text = "\n".join([f"- {bullet}" for bullet in bullets])
        
        prompt = f"""Here are my existing resume bullets:
{bullets_text}

Here is a job description:
{job_description}

Rewrite only the bullets to better match terminology and priorities in the JD.
Do not invent skills or experience.
Keep length similar.
Make it sound natural and human - avoid corporate jargon overload.
Return only the bullet points, one per line, starting with a dash (-)."""

        try:
            print("  🤖 Optimizing bullets with AI...")
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional resume writer who creates natural, human-sounding resume bullets that match job descriptions without inventing experience or using excessive corporate speak."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            optimized_text = response.choices[0].message.content.strip()
            # Parse the bullets from the response
            optimized_bullets = []
            for line in optimized_text.split('\n'):
                line = line.strip()
                if line.startswith('-'):
                    optimized_bullets.append(line[1:].strip())
                elif line and not line.startswith('#'):
                    optimized_bullets.append(line)
            
            return optimized_bullets if optimized_bullets else bullets
            
        except Exception as e:
            print(f"  ⚠️  AI optimization failed: {e}")
            return bullets
    
    def optimize_summary_with_ai(self, summary, job_description):
        """Use AI to optimize professional summary to match job description"""
        if not self.use_ai or not self.openai_client:
            return summary
        
        prompt = f"""Here is my current professional summary:
{summary}

Here is a job description I'm applying for:
{job_description}

Rewrite my professional summary to better align with this job description.
Do not invent skills or experience I don't have.
Keep it concise (2-3 sentences).
Make it sound natural and authentic, not overly corporate or buzzword-heavy.
Return only the rewritten summary."""

        try:
            print("  🤖 Optimizing professional summary with AI...")
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional resume writer who creates natural, authentic professional summaries that align with job descriptions without inventing experience."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            optimized_summary = response.choices[0].message.content.strip()
            return optimized_summary
            
        except Exception as e:
            print(f"  ⚠️  AI optimization failed: {e}")
            return summary
    
    def customize_for_job(self, job_description, company_info):
        """Customize base data for specific job application"""
        # Deep copy to avoid modifying original
        import copy
        customized_data = copy.deepcopy(self.base_data)
        
        # Get full job description text
        job_desc_text = job_description.get('description', '')
        if job_description.get('requirements'):
            job_desc_text += "\n\nRequirements:\n" + "\n".join(job_description.get('requirements', []))
        
        # AI-optimize summary if enabled
        if self.use_ai and 'summary' in customized_data:
            customized_data['summary'] = self.optimize_summary_with_ai(
                customized_data['summary'],
                job_desc_text
            )
        
        # AI-optimize experience bullets if enabled
        if self.use_ai and 'experience' in customized_data:
            for exp in customized_data['experience']:
                if 'responsibilities' in exp:
                    exp['responsibilities'] = self.optimize_resume_bullets_with_ai(
                        exp['responsibilities'],
                        job_desc_text
                    )
        
        # Add job info to the data
        customized_data['job_info'] = {
            'title': job_description.get('title', ''),
            'company': company_info.get('name', ''),
            'description': job_description.get('description', ''),
            'requirements': job_description.get('requirements', []),
            'company_about': company_info.get('about', ''),
            'company_website': company_info.get('website', '')
        }
        return customized_data
    
    def generate_resume(self, data, output_path):
        """Generate PDF resume from data"""
        template = self.template_env.get_template('resume_template.html')
        html_content = template.render(**data)
        
        # Convert HTML to PDF
        HTML(string=html_content).write_pdf(output_path)
        print(f"✓ Resume generated: {output_path}")
    
    def generate_cover_letter(self, data, output_path):
        """Generate PDF cover letter from data"""
        template = self.template_env.get_template('cover_letter_template.html')
        html_content = template.render(**data)
        
        # Convert HTML to PDF
        HTML(string=html_content).write_pdf(output_path)
        print(f"✓ Cover letter generated: {output_path}")
    
    def create_application_folder(self, company_name):
        """Create folder structure for job application"""
        # Sanitize folder name
        safe_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_name = safe_name.replace(' ', '_')
        
        # Create timestamped folder
        timestamp = datetime.now().strftime('%Y%m%d')
        folder_name = f"applications/{safe_name}_{timestamp}"
        folder_path = Path(folder_name)
        folder_path.mkdir(parents=True, exist_ok=True)
        
        return folder_path
    
    def process_application(self, job_file, company_file=None):
        """Main process to generate all documents for a job application"""
        # Load job and company information (can be JSON or plain text)
        # Support both merged format and separate files
        if company_file is None:
            # Load merged format
            merged_data = self.load_input_file(job_file, 'merged')
            if isinstance(merged_data, dict) and 'job' in merged_data and 'company' in merged_data:
                job_description = merged_data['job']
                company_info = merged_data['company']
                print("✓ Loaded merged job and company data from single file")
            else:
                raise ValueError("Merged file must contain 'job' and 'company' sections")
        else:
            # Load separate files (backwards compatibility)
            job_description = self.load_input_file(job_file, 'job')
            company_info = self.load_input_file(company_file, 'company')
        
        # Customize data for this job
        customized_data = self.customize_for_job(job_description, company_info)
        
        # Create application folder
        company_name = company_info.get('name', 'Company')
        output_folder = self.create_application_folder(company_name)
        
        # Generate documents
        resume_path = output_folder / "resume.pdf"
        cover_letter_path = output_folder / "cover_letter.pdf"
        
        self.generate_resume(customized_data, str(resume_path))
        self.generate_cover_letter(customized_data, str(cover_letter_path))
        
        # Save customized data for reference
        customized_data_path = output_folder / "customized_data.json"
        with open(customized_data_path, 'w', encoding='utf-8') as f:
            json.dump(customized_data, f, indent=4)
        
        # Copy base data to folder for archival
        base_data_copy = output_folder / "base_data_snapshot.json"
        shutil.copy(self.base_data_file, base_data_copy)
        
        # Save the parsed job and company info
        job_info_path = output_folder / "parsed_job_description.json"
        with open(job_info_path, 'w', encoding='utf-8') as f:
            json.dump(job_description, f, indent=4)
        
        company_info_path = output_folder / "parsed_company_info.json"
        with open(company_info_path, 'w', encoding='utf-8') as f:
            json.dump(company_info, f, indent=4)
        
        print(f"\n✓ Application package created in: {output_folder}")
        print(f"  - resume.pdf")
        print(f"  - cover_letter.pdf")
        print(f"  - customized_data.json")
        print(f"  - base_data_snapshot.json")
        print(f"  - parsed_job_description.json")
        print(f"  - parsed_company_info.json")
        
        return output_folder
    
    def load_input_file(self, file_path, input_type):
        """Load input file - can be JSON or plain text"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to parse as JSON first
        try:
            data = json.loads(content)
            if input_type == 'merged':
                print(f"✓ Loaded merged data from JSON file")
            else:
                print(f"✓ Loaded {input_type} data from JSON file")
            return data
        except json.JSONDecodeError:
            # It's plain text, parse with AI
            if input_type == 'merged':
                raise ValueError("Merged format must be JSON")
            print(f"📄 Detected plain text {input_type} file, parsing with AI...")
            if input_type == 'job':
                return self.parse_job_description_with_ai(content)
            elif input_type == 'company':
                return self.parse_company_info_with_ai(content)
            else:
                raise ValueError(f"Unknown input type: {input_type}")


def main():
    parser = argparse.ArgumentParser(description='Generate customized resume and cover letter')
    parser.add_argument('--job', '-j', required=True, help='Path to job file (JSON with company and job sections, or plain text). Use merged format: {"company": {...}, "job": {...}}')
    parser.add_argument('--company', '-c', help='Path to separate company info file (optional, for backwards compatibility)')
    parser.add_argument('--base', '-b', default='inputs/base_data.json', help='Path to base data JSON file (default: inputs/base_data.json)')
    parser.add_argument('--use-ai', action='store_true', help='Enable AI optimization for resume customization (requires OPENAI_API_KEY)')
    
    args = parser.parse_args()
    
    # Check if required files exist
    if not os.path.exists(args.job):
        print(f"Error: Job file not found: {args.job}")
        return
    
    if args.company and not os.path.exists(args.company):
        print(f"Error: Company info file not found: {args.company}")
        return
    
    # Create CV Creator instance
    use_ai = args.use_ai
    creator = CVCreator(args.base, use_ai=use_ai)
    
    print("📝 CV Creator initialized")
    if creator.use_ai:
        print("🤖 AI optimization enabled - resumes will be customized for the job")
    else:
        print("⚡ AI optimization disabled - using base resume data")
    if args.company:
        print("📄 Using separate job and company files (legacy mode)\n")
    else:
        print("📄 Using merged job file format\n")
    
    # Process application
    creator.process_application(args.job, args.company)


if __name__ == "__main__":
    main()
