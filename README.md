# Prayer Request Community App

This project is a web application designed to help individuals share prayer requests and receive beautifully crafted prayers from an AI-powered spiritual guide. The system generates both **personal** and **community** versions of each prayer, allowing users to choose which version to share publicly while maintaining access to both perspectives.

## Features

- **Dual Prayer Generation:**  
  For every prayer request, the AI generates:
  - A **personal prayer** (first-person, for the requester)
  - A **community prayer** (third-person, for group prayer)
- **User Choice:**  
  Users can select which version (personal or community) to display publicly.
- **Empathetic, Inclusive Prayers:**  
  Prayers are generated using non-denominational, inclusive language, with references to scripture and a focus on comfort, hope, and spiritual growth.
- **Prayer Request Submission:**  
  Users can submit requests, which are then transformed into prayers suitable for both personal reflection and community support.

## How It Works

1. **Submit a Prayer Request:**  
   Users provide their name and a description of their prayer need.
2. **AI Prayer Generation:**  
   The backend uses prompt templates (`prayer_prompt.txt` for community, `personal_prayer_prompt.txt` for personal) to instruct the AI to generate two versions of the prayer.
3. **Store and Display:**  
   Both versions are saved in the database. By default, the community version is shown publicly, but the author can switch to the personal version.
4. **Community Engagement:**  
   The community can view and pray for requests, using the version chosen by the author.

## File Structure

- `main.py`  
  Core backend logic, including database models and API endpoints for prayer submission and version selection.
- `ai_service.py`  
  Handles AI prompt construction and response parsing for both prayer versions.
- `prayer_prompt.txt`  
  Prompt template for generating community prayers.
- `personal_prayer_prompt.txt`  
  Prompt template for generating personal prayers.
- `dual_prayer_generation_plan.md`  
  Development plan outlining the dual generation system and API changes.

## Development Plan

See `dual_prayer_generation_plan.md` for a detailed breakdown of the implementation phases, including database schema updates, AI service enhancements, and API endpoint changes.

## Getting Started

1. **Clone the repository**
2. **Install dependencies** (see requirements in your Python environment)
3. **Run the backend** (typically with `python main.py`)
4. **Submit prayer requests and experience dual prayer generation!**

## Contributing

Contributions are welcome! Please see the development plan for areas to help, or open an issue to discuss new features.

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0). See the [LICENSE](LICENSE) file for the full license text.

The AGPL license ensures that:
- Users have the freedom to run, study, share, and modify the software
- Any modifications must also be licensed under the AGPL
- If the software is used over a network (like a web application), users must have access to the source code
- All derivative works must maintain the same freedoms

This license is particularly suitable for web applications like this prayer request community app, as it ensures that any hosted versions of the software remain open source and accessible to the community.

---
