# MapAssist
Demo: https://youtu.be/TWpHDfd3G_8

Presentation: https://youtu.be/MEvwDrE6cGs?si=S1QjL26RDE_Y5YCV

Use it here: https://map-assist.streamlit.app/

A watsonx AI based web application to help people in distress during a disaster.

## Installation
1. Have a Python3 installation ready
	- Refer [this doc](https://www.python.org/downloads/) to install 
2. Create a python virtual environment with pip. Example, `python3 -m venv mapassist`
3. Activate virtual environment, Example, `source <path to virtual env bin>`
4. Change to the project root and install requirements, `pip install -r requirements.txt`
5. Run the app using `streamlit run app.py`
6. Go to the following address in the browser, http://127.0.0.1:8501


## Application Flow

1. Ask for user location (browser permission) => User lat long
2. Based on their location, we check if there is an ongoing disaster (in our db) and if they need  immediate care => Ask and redirect to 911 for critical issues
2. User starts chat
	- can type raw text or select top suggested questions (hard-coded)
		- determine a severity score using simple LLM with defined prompt
	- based on score we have 3 separate flows and we also bucketize the user's distress into predefined buckets
		- may ask follow up questions if needed

Flow 1 => CRITICAL => Redirect to government agencies / 911. 

Flow 2 => Low => Awarness based queries
	- We identify requires resources based on user's query (vector database)
	- Feed data into RAG and ask for query resulution + Follow up chat OR Restart flow
	- Response can be summarized or may have interactive resources

Flow 3 => Medium (Community support)
	- Based on bucket of problem, identify personnels in the community who can help (show in map)
	- User can probably further describe their probllem and we can further filter the set of results in our database

 ## Inspiration


A UN study found that many disasters share root causes, notably poor governance, and that their impacts are interconnected. Addressing these links could help mitigate disaster effects. Researchers highlighted eight key strategies for disaster risk reduction: aligning with natural processes, fostering innovation, collaboration, securing livelihoods, adjusting consumption, strengthening governance, risk planning, and enhancing early warning systems. Our product targets five of these areas. A major challenge in disaster management is a lack of context-specific solutions and overgeneralization, often missing traditional knowledge. Our chatbot provides tailored, local solutions, leveraging "Distributed Help," where individuals assist nearby volunteers, reducing response times effectively.

Additionally, we address mental health needs. A study published by the NIH indicates that mental health disorders can affect up to 87.6% of individuals during a disaster. Enhancing community resilience, improving healthcare access, and implementing suitable mitigation strategies can improve outcomes for vulnerable populations. By fostering a sense of community, MAPAssist aims to lower these rates and provide vital support.

## What it does

MAPAssist: Our app is designed to provide customized assistance during disasters. When users face a crisis, the app guides them on what steps to take based on the specific type of disaster they are experiencing. If a user requires essential resources—such as food, medical supplies, or services like medical consultations—the app pinpoint locations nearby where they can access these resources. These locations often belong to their neighbors, fostering community support.

To facilitate this, we maintain a comprehensive dataset of volunteers who are willing to help. Anyone can sign up as a volunteer, offering their skills or extra resources to assist others in need. When someone requires assistance, the app quickly maps them to the nearest available volunteer who can provide the necessary support. In essence, our app connects individuals in crisis with their local community, ensuring timely assistance and enhancing resilience during emergencies.

## How we built it

- Streamlit
- Watson AI (IBM watsonx functions, foundation models, vector indexes, and RAG-Retrieval-Augmented Generation)
- Languages: Python, HTML, CSS
- APIs: Watsonx


## Challenges We Encountered

- Learning Curve with Streamlit: Streamlit was a new framework for us, requiring time to familiarize ourselves with its features.

- Adaptation to WatsonxAI: While WatsonxAI was also new, its intuitive functionality allowed us to quickly get up to speed.

- Prompt Engineering: Fine-tuning foundational models through prompt engineering was essential to ensure we received customized, prompt responses.

- Integration Issues: Establishing a seamless connection between our Streamlit app and WatsonxAI presented some technical challenges.


## Accomplishments We're Proud Of

- *Cross-Department Collaboration*: Successfully worked together across departments.
- *Rapid Development*: Built an AI-driven platform in just two days while learning Watson AI and Streamlit.
- *Broad Audience Impact*: Created a tool designed to assist a wide range of users during natural disasters.

## What We Learned

- *Understanding Watsonx AI*: Gained insights into the intuitive capabilities of the Watsonx AI platform.
- *Value of Collaboration*: Recognized the importance of teamwork and a results-driven mindset.

## What's Next for MAPAssist

- *Expanded Volunteer Data Collection*: Scaling volunteer data acquisition to reach a larger audience.
- *Broader Scalability*: Enhancing the tool’s capabilities beyond urban areas.
- *Natural Calamity Predictions*: Developing predictive features for natural disasters.
- *Integration with Local Authorities*: Collaborating with local agencies to assist those in distress.


Additional features
- Geo tagged images (uploaded by people)
- Queries heatmap
- Disaster heatmap
- Mental distress + Peer interaction
- Check on the critical ones also
