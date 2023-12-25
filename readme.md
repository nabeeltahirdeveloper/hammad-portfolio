/portfolio_website/                 # Root directory
│
├── app.py                          # Main Flask application file
├── config.py                       # Configuration settings
│
├── /templates/                     # HTML templates directory
│   ├── home.html                   # Homepage template
│   ├── login.html                  # Admin login page template
│   ├── register.html               # Admin registration page template
│   ├── admin_panel.html            # Admin panel template
│   ├── skills.html                 # Skills page template
│   ├── projects.html               # Projects page template
│   ├── publications.html           # Publications page template
│   ├── experiences.html            # Experiences page template
│   ├── education.html              # Education details template
│   ├── resume.html                 # Resume template
│   └── error.html                  # Error page template
│
├── /static/                        # Static files directory
│   ├── /css/
│   │   └── style.css               # Main CSS stylesheet
│   ├── /js/
│   │   └── script.js               # JavaScript file (optional)
│   └── /images/                    # Directory for images
│       └── [image files]
│
├── /models/                        # Database models (optional)
│   ├── user.py                     # User model
│   ├── skills.py                   # Skills model
│   ├── projects.py                 # Projects model
│   ├── publications.py             # Publications model
│   ├── experiences.py              # Experiences model
│   └── education.py                # Education model
│
├── init_db.py                      # Database initialization script (optional)
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git ignore file
└── README.md                       # Project documentation
