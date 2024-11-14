import requests
import pandas as pd
import numpy as np
from users_data import users

# users = {}

# Constants for API credentials
app_id = '3f2e39f4'
app_key = '8cf29a29cf3001f13dd12671773ff9d9'
country = 'za'

# Job retrieval URL
url = f'http://api.adzuna.com/v1/api/jobs/{country}/search/1?app_id={app_id}&app_key={app_key}&content-type=application/json'

def fetch_jobs(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['results']
    else:
        print(f"Error fetching jobs: {response.status_code}")
        exit()
    
# Extract relevant fields from job data
def parse_job_data(jobs):
    headers = ['title', 'description', 'category', 'company', 'contract_type', 'redirect_url', 'created', 'location']
    jobs_data = []
    for job in jobs:
        job_listing = {}
        for header in headers:
            if header in job:
                if header == 'location' and isinstance(job[header], dict):
                    job_listing[header] = ', '.join(job[header].get('area', []))
                elif header == 'category' and isinstance(job[header], dict):
                    job_listing[header] = job[header].get('label', 'Not available')
                elif header == 'company' and isinstance(job[header], dict):
                    job_listing[header] = job[header].get('display_name', 'Not available')
                else:
                    job_listing[header] = job.get(header, 'Not available')
        jobs_data.append(job_listing)
    return pd.DataFrame(jobs_data)


def get_coordinates(location):
    url = "https://nominatim.openstreetmap.org/search"

    params = {
        'q': location, # Address to geocode
        'format': 'json',
    }
    
    headers = {
        'User-Agent': 'N/A/1.0 (phethegomotidi@gmail.com)'
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data:
              return float(data[0]['lat']), float(data[0]['lon'])
    return None

def calc_distance(user_coordinates, business_coordinates):
    if not user_coordinates and business_coordinates:
        return None
    
    start = f'{user_coordinates[1]},{user_coordinates[0]}'  # Longitude, Latitude
    end = f'{business_coordinates[1]},{business_coordinates[0]}'  # Longitude, Latitude
    url = f"http://router.project-osrm.org/route/v1/driving/{start};{end}"
    params = {"overview": "full", "geometries": "geojson"}

    response = requests.get(url, params=params)

    if response.status_code == 200:
        route_data = response.json()
        return route_data['routes'][0]['distance']
    return None
    
def get_user_category(jobs_df):
  categories = list(jobs_df['category'].unique())
  for index, category in enumerate(categories):
     print(f'{index+1}. {category}')

  user_job = input(' ').lower().strip()

  if user_job.isnumeric():
    category = categories[int(user_job)-1]
    return category
  return ''
  
  # categories = list(jobs_df['category'].unique()) + list(jobs_df['title'].unique())
  # for category in categories:
  #   if user_job in category.lower():
  #     return category
  # print("Category not found.")
  # return ''

# Find nearby job locations based on distance
def get_user_location(jobs_df, user_location):
  # user_location = input('Location?  ').lower().strip()
  print('\nThis may take a few minutes...\n')
  user_coordinates = get_coordinates(user_location)
  
  if user_coordinates:
    locations_within_distance = []
  
    for loc in jobs_df['location'].unique():
      business_coordinates = get_coordinates(str(loc))
      if business_coordinates:
        distance = calc_distance(user_coordinates, business_coordinates)
        if distance is not None and float(distance) <= 60000:
          locations_within_distance.append(str(loc))

    return locations_within_distance
  else:
      return []
  
def seeking_skills():
  def suggest_skills():
      skill_requirements = {
          'Developer': ['Python', 'JavaScript', 'SQL'],
          'Marketing': ['Digital Marketing', 'Content Writing', 'SEO'],
          'Data Analyst': ['SQL', 'Python', 'Data Visualization', 'Statistics', 'Excel'],
          'UI/UX Designer': ['Adobe XD', 'Figma', 'User Research', 'Wireframing', 'Prototyping'],
          'Project Manager': ['Agile Methodologies', 'Scrum', 'Team Management', 'Project Planning', 'Risk Management'],
          'Human Resources': ['Recruitment', 'Employee Relations', 'HRIS', 'Payroll', 'Compliance'],
          'Customer Support': ['Communication Skills', 'Problem Solving', 'CRM Software', 'Empathy', 'Time Management'],
          'Finance': ['Financial Analysis', 'Excel', 'Accounting', 'Budgeting', 'Risk Management'],
          'Operations': ['Process Optimization', 'Inventory Management', 'Supply Chain Management', 'Logistics', 'Quality Control'],
          'Software Tester': ['Automated Testing', 'Manual Testing', 'Selenium', 'JIRA', 'Bug Tracking'],
          'Sales': ['Lead Generation', 'Negotiation', 'CRM Software', 'Cold Calling', 'Market Research'],
          'Content Creation': ['Content Strategy', 'Video Editing', 'Copywriting', 'Graphic Design', 'Social Media Management'],
          'DevOps': ['CI/CD', 'AWS', 'Docker', 'Kubernetes', 'Linux Administration'],
          'Machine Learning Engineer': ['Python', 'TensorFlow', 'Machine Learning', 'Data Science', 'Model Deployment'],
          'Cybersecurity': ['Network Security', 'Penetration Testing', 'Risk Assessment', 'Incident Response', 'Compliance'],
          'Healthcare': ['Medical Terminology', 'Patient Care', 'Healthcare Administration', 'EMR Software', 'HIPAA Compliance'],
          'Legal': ['Legal Research', 'Contract Law', 'Document Drafting', 'Negotiation', 'Case Management'],
          'Admin': ['Microsoft Office', 'Data Entry', 'Scheduling', 'Time Management', 'Organization Skills'],
          'Sales': ['Lead Generation', 'Customer Relationship Management (CRM)', 'Negotiation', 'Market Research', 'Cold Calling'],
          'Engineering': ['Problem Solving', 'Technical Drawing', 'CAD Software', 'Project Management', 'Analytical Skills'],
          'Teaching': ['Lesson Planning', 'Classroom Management', 'Curriculum Development', 'Student Assessment', 'Communication Skills'],
          'Accounting': ['Financial Reporting', 'Bookkeeping', 'Tax Preparation', 'Auditing', 'Excel'],
          'Retail': ['Customer Service', 'Sales Techniques', 'Inventory Management', 'POS System Operation', 'Merchandising']
      }
      categories = list(skill_requirements.keys())
      for index, category in enumerate(categories):
         print(f'{index + 1}. {category}')
      user_category = input()
      if user_category.isnumeric():
        category = categories[int(user_category)-1]
      else:
         print('Invalid input')
         exit()

      missing_skills = skill_requirements.get(category, [])
      return category, missing_skills

  def display_recommendations():
      user_category, suggested_skills = suggest_skills()
      if suggested_skills:
          print(f"To improve your chances for {user_category} jobs, consider learning: {', '.join(suggested_skills)}")
      else:
          print("No specific skill recommendations at this time.")
  display_recommendations()

def seeking_course():
  def suggest_micro_courses():
    course_recommendations = {
        'Developer': ['Intro to Python', 'Web Development Basics', 'Database Management'],
        'Marketing': ['Digital Marketing 101', 'Content Strategy', 'Social Media Management'],
        'Data Analyst': ['Data Analysis with Python', 'SQL for Data Science', 'Data Visualization with Tableau'],
        'UI/UX Designer': ['Intro to UX Design', 'Figma for Beginners', 'User Research Fundamentals'],
        'Project Manager': ['Agile Project Management', 'Project Planning and Scheduling', 'Risk Management Essentials'],
        'Human Resources': ['HR Fundamentals', 'Employee Relations and Engagement', 'Payroll Administration'],
        'Customer Support': ['Customer Service Basics', 'Effective Communication Skills', 'Time Management for Support Teams'],
        'Finance': ['Financial Analysis for Beginners', 'Excel for Finance', 'Intro to Accounting'],
        'Operations': ['Supply Chain Fundamentals', 'Inventory Management Essentials', 'Quality Control in Operations'],
        'Software Tester': ['Software Testing Foundations', 'Automated Testing with Selenium', 'Bug Tracking with JIRA'],
        'Sales': ['Sales Fundamentals', 'Negotiation Skills', 'CRM Software Training'],
        'Content Creation': ['Content Strategy Basics', 'Intro to Video Editing', 'Copywriting for Beginners'],
        'DevOps': ['Intro to DevOps', 'Docker and Kubernetes Fundamentals', 'AWS for DevOps'],
        'Machine Learning Engineer': ['Machine Learning with Python', 'TensorFlow Basics', 'Model Deployment Techniques'],
        'Cybersecurity': ['Intro to Cybersecurity', 'Network Security Fundamentals', 'Penetration Testing Basics'],
        'Healthcare': ['Medical Terminology', 'Intro to Healthcare Administration', 'EMR Software Training'],
        'Legal': ['Legal Research Fundamentals', 'Contract Law Essentials', 'Case Management Techniques'],
        'Admin': ['Microsoft Office Specialization', 'Effective Time Management', 'Business Communication Skills'],
        'Sales': ['Sales Fundamentals', 'Customer Relationship Management (CRM)', 'Cold Calling Techniques'],
        'Engineering': ['Intro to CAD Software', 'Problem Solving for Engineers', 'Technical Drawing Basics'],
        'Teaching': ['Lesson Planning and Development', 'Classroom Management', 'Student Assessment Strategies'],
        'Accounting': ['Intro to Accounting', 'Tax Preparation Essentials', 'Financial Reporting with Excel'],
        'Retail': ['Customer Service Basics', 'Inventory Management', 'POS System Training']


    }
    course_category = list(course_recommendations.keys())
    for index, course in enumerate(course_category):
       print(f'{index+1}. {course}')
    user_category = input() 
    if user_category.isnumeric():
        category = course_category[int(user_category)-1]
    else:
         print('Invalid input')
         exit()

    return category, course_recommendations.get(category, [])

  def display_course_suggestions():
      user_category, courses = suggest_micro_courses()
      if courses:
          print(f"Consider taking these courses to improve your skills for {user_category} roles: {', '.join(courses)}")
      else:
          print("No additional course recommendations at this time.")
          
  display_course_suggestions()

def offer_entrepreneurship_resources():
    resources = {
        'Micro-Business Basics': 'Learn about creating a small business with low startup costs.',
        'Financial Literacy': 'Understand budgeting, saving, and investing.',
        'Local Microfinance Options': 'Find microfinance options near you to fund your business idea.'
    }
    print("Entrepreneurship Resources:\n")
    for topic, description in resources.items():
        print(f"{topic}: {description}")

def track_user_progress(user_name):
    points_system = {
        'completed_application': 10,
        'completed_course': 20
    }
    print('\n1. Completed application')
    print('2. Completed course')
    user_input = input()
    if user_input == '1':
      action = 'completed_application'
    elif user_input == '2':
      action = 'completed_course'
    else:
      print('Invalid input')
      exit()
    if user_name not in users:
        users[user_name] = users.get(user_name, 0) + points_system.get(action, 0)
    else:
       users[user_name] += users.get(user_name, 0) + points_system.get(action, 0)
       
    print(f"{user_name}'s progress updated. Points: {users[user_name]}")
      
# Main execution logic
def seeking_job():
    # Fetch and parse job data
    jobs = fetch_jobs(url)
    jobs_df = parse_job_data(jobs)

    # Clean and replace missing data
    jobs_df.replace(np.nan, 'Not available', inplace=True)
    jobs_df.replace(r'^\s*$', np.nan, regex=True, inplace=True)
    jobs_df.dropna(inplace=True)
    jobs_df.reset_index(drop=True, inplace=True)
    # print(jobs_df[['category', 'location']])

    # User input and filtering
    user_category = get_user_category(jobs_df)
    user_location = input("Location? (Enter location or 'No' or 'n') : ").strip().lower()
    print(user_location)
    if user_location == 'no' or user_location == 'n':
       print(user_location)
       user_location_found = []
    else:
      user_location_found = get_user_location(jobs_df, user_location)

    # Filter jobs by user location and category
    filtered_jobs = jobs_df
    if user_category:
      filtered_jobs = filtered_jobs[
        (filtered_jobs['category'].str.contains(user_category, case=False) | filtered_jobs['title'].str.contains(user_category, case=False))
        ]
    
    if user_location_found:
      filtered_jobs = filtered_jobs[
        filtered_jobs['location'].isin(user_location_found) 
      ]
    if user_location_found and user_category:
      filtered_jobs = jobs_df[
        (jobs_df['category'].str.contains(user_category, case=False) | jobs_df['title'].str.contains(user_category, case=False)) &
        jobs_df['location'].str.contains(user_location, case=False)
      ]

    if filtered_jobs.empty:
      print('No jobs found.')
      exit()

    filtered_df = filtered_jobs[['category', 'title', 'company', 'location', 'contract_type', 'description', 'redirect_url', 'created']]

    def create_job_str(row):
        description = row['description'].replace('\n', '. ')
        return (
            f'\nJob Title: {row["title"]}\n'
            f'Company: {row["company"]}\n'
            f'Location: {row["location"]}\n'
            f'Contract Type: {row["contract_type"]}\n'
            f'Description: {description}\n'
            f'Date Posted: {row["created"][:10]}\n'
            f'URL: {row["redirect_url"]}\n'
        )

    user_output = '\n\n'.join(filtered_df.apply(create_job_str, axis=1).to_list())
    print(user_output if user_output else 'No jobs found.')

def main():
  print('Welcome to Phanda Ispani.\n')
  user_name = input('Enter your name: ')
  # user_ID = input('Enter your ID (any username): \n')

  print('\nChoose 1-4:')
  print('1. Seeking jobs')
  print('2. Seeking skills')
  print('3. Seeking courses')
  print('4. Seeking entrepreneurship resources')
  print('5. Update user progress')
  user_input = input()

  if user_input == '1':
    print('\n')
    seeking_job()
  elif user_input == '2':
    print('\n')
    seeking_skills()
  elif user_input == '3':
    print('\n')
    seeking_course()
  elif user_input == '4':
    print('\n')
    offer_entrepreneurship_resources()
  elif user_input == '5':
    print('\n')
    # action = input('Enter completed pplication or completed_course: ')
    track_user_progress(user_name)
  else:
    print('\n')
    print('Invalid input')
  exit()

if __name__ == '__main__':
   main()
  

   




if __name__ == "__main__":
    main()