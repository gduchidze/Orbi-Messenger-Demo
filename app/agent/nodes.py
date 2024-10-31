import asyncio
import json
import logging
from uuid import uuid4

import aiohttp
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from app.agent.interface import AgentState, quick_buttons
from app.agent.tools import tools
from app.config import settings
from app.messenger import messenger_client


class OrbiAgentNode:
    async def __call__(self, state: AgentState, config):
        logging.info("---CALL AGENT---")
        logging.info(f"Config received: {config}")

        messages = state.messages
        logging.info(f"Messages received: {messages}")

        msg = messages[-1].content
        logging.info(f"Processing message content: {msg}")

        message_type = config.get("configurable", {}).get("message_type")
        logging.info(f"Message type: {message_type}")

        if message_type == "postback":
            logging.info(f"Handling postback: {msg}")


        sender_id = config.get("configurable", {}).get("thread_id")
        async def get_user_name(user_id: str) -> str:
            url = f"https://graph.facebook.com/{user_id}?fields=first_name&access_token={settings.messenger_page_access_token}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("first_name", "")
                    return ""

        user_name = await get_user_name(sender_id) if sender_id else ""
        carousel_elements =  [
                {
                    "title": "🏢 Central Park Towers-ში ინვესტიცია",
                    "image_url": "https://www.cpt.ge/storage/gallery_image/187/iJ0r078pR4pvfuYT8PQdpRm1j5rtqaGGclxOe3na.jpg",  # შეცვალეთ რეალური URL-ით
                    "buttons": [{
                        "type": "postback",
                        "title": "არჩევა",
                        "payload": "1. არჩევა"
                    }]
                },
                {
                    "title": "ℹ️ პროექტის შესახებ",
                    "image_url": "https://img.freepik.com/free-photo/engineer-meeting-architectural-project-working-with-partner_1421-72.jpg?t=st=1730274181~exp=1730277781~hmac=8c582eec415db679474fb0fe708a735e1dcfce70842aae6c147b3be908411dac&w=1800",
                    "buttons": [{
                        "type": "postback",
                        "title": "არჩევა",
                        "payload": "2. არჩევა"
                    }]
                },
                {
                    "title": "📄 კონტრაქტი და იურიდიული საკითხები",
                    "image_url": "https://img.freepik.com/free-photo/boss-handshaking-offering-employment-agreement_1163-5300.jpg?t=st=1730274230~exp=1730277830~hmac=85322e8e759aa1913d7d3fa636a6f9af5ea13e0bed5c45c27ced2bf42e98b836&w=1800",  # შეცვალეთ რეალური URL-ით
                    "buttons": [{
                        "type": "postback",
                        "title": "არჩევა",
                        "payload": "3. არჩევა"
                    }]
                },
                {
                    "title": "💰 ინვესტიციაზე, ფასსა და შემოსავალზე",
                    "image_url": "https://img.freepik.com/free-photo/digital-increasing-bar-graph-with-businessman-hand-overlay_53876-97640.jpg?t=st=1730274184~exp=1730277784~hmac=e1578b3ea4634b59cfb0725fdc7c6d95fd30f30ddf5efa248c57624ef68b6a70&w=2000",  # შეცვალეთ რეალური URL-ით
                    "buttons": [{
                        "type": "postback",
                        "title": "არჩევა",
                        "payload": "4. არჩევა"
                    }]
                }
            ]

        if  msg == '🏢 Central Park Towers-ში ინვესტიცია' or msg == 'დიახ' or msg == "1. არჩევა":
            logging.info(f"[Central Park Towers Button] Message: {msg}")
            return {
                "messages": [AIMessage(
                    content=f" 🙏 მადლობა {user_name} დაინტერესებისთვის, დაგვიტოვეთ საკონტაქტო ნომერი და ჩვენი გაყიდვების გუნდი დაგიკავშირდებათ."
                )],
                "suppress_response": False
            }


        elif msg == "არა":
            async def send_carousel():
                await asyncio.sleep(1.5)
                await messenger_client.send_generic_template(sender_id, carousel_elements)
            return_value = {
                "messages": [AIMessage(content="🤖 გთხოვთ აირჩიოთ რით შემიძლია დაგეხმაროთ:")],
                "suppress_response": False
            }
            asyncio.create_task(send_carousel())
            return return_value
        elif msg == "📄 კონტრაქტი და იურიდიული საკითხები" or msg == "3. არჩევა":
            return {
                "messages": [AIMessage(
                    content=f"🌟 მადლობა {user_name} დაინტერესებისთვის, დაგვიტოვეთ საკონტაქტო ნომერი და ჩვენი იურისტების გუნდი დაგიკავშირდებათ."
                )],
            }

        elif msg == "ℹ️ პროექტის შესახებ" or msg == "2. არჩევა":
            project_buttons = [
                "ინფრასტრუქტურა",
                "დასრულების თარიღი",
                "შეძენის პირობები",
            ]
            return {
                "messages": [AIMessage(content="🏗️ Central Park Towers არის 5 ვარსკვლავიანი ინტეგრირებული საკურორტო-სასტუმრო კომპლექსი, რომელიც მდებარეობს ალექსანდრე ყაზბეგის გამზირზე, თბილისის ცენტრალურ პარკთან ახლოს.კომპლექსი იმყოფება Radisson Blu-ს მმართველობის ქვეშ. ინფრასტრუქტურას კი წარმოდგენს, მასპინძლობის, კვების, შოპინგის და გართობის სფეროში ცნობილი საერთაშორისო ბრენდები. დეტალური ინფორმაციისთვის, გთხოვთ აირჩიოთ თემა")],
                "quick_replies": quick_buttons(project_buttons)
            }

        elif "ინფრასტრუქტურა" in msg:

            project_buttons = [
                "დიახ",
                "არა"
            ]
            return {
                "messages": [AIMessage(
                    content="🎆 Central Park Towers-ის ინფრასტრუქტურა მოიცავს: საერთაშორისო ბრენდის 7 რესტორანს საქართველოში პირველ პრემიუმ კლასის სავაჭრო ცენტრს, Harvey Nichols-ის მმართველობით რეგიონში უდიდეს მულტიფუნქციურ დარბაზს, ღონისძიებების გასამართად, რომელიც იტევს 2500 ადამიანს საქართველოში უდიდეს კაზინოს, რომელიც იმართება მაკაოდან პრემიუმ კლასის სპა და გამაჯანსაღებელ ცენტრებს Spa Soul-ის მმართველობით ფართო პარკინგსა და თანამედროვე საოფისე სივრცეებს. გაქვს დამატებითი კითხვები?"
                )],
                "quick_replies": quick_buttons(project_buttons)
            }

        elif "დასრულების თარიღი" in msg:

            project_buttons = [
                "დიახ",
                "არა"
            ]
            return {
                "messages": [AIMessage(
                    content="🗓️ Central Park Towers-ი აქტიური შენების პროცესშია, რომელიც 2025 წლის დეკემბერში დასრულდება, რაც გულისხმობს სასტუმროს ნომრებისა და სხვა ობიექტების მთლიანად კეთილმოწყობას. გაქვს დამატებითი კითხვები?"
                )],
                "quick_replies": quick_buttons(project_buttons)
            }

        elif "შეძენის პირობები" in msg:

            project_buttons = [
                "დიახ",
                "არა"
            ]
            return {
                "messages": [AIMessage(
                    content="🏢 სასტუმროს ნომრის შეძენა მარტივია. თქვენ შეგიძლიათ გადაიხადოთ თანხა მთლიანად ან აირჩიოთ ჩვენი გადახდის ერთ-ერთი მოქნილი მეთოდი, რომელიც გთავაზობთ პირველად შენატანს 35%-ის ოდენობით, ხოლო დარჩენილ თანხას შემოიტანთ ყოველთვიურად მშენებლობის დროს. ან შეგიძლიათ ისარგებლოთ საბანკო კრედიტით, რომელსაც გადაანაწილებთ 60 თვეზე წინასწარი გადახდის საკომისიოს გარეშე. გაქვს დამატებითი კითხვები?"
                )],
                "quick_replies": quick_buttons(project_buttons)
            }


        elif msg == "💰 ინვესტიციაზე, ფასსა და შემოსავალზე" or msg == "4. არჩევა":
            investment_buttons = [
                "ინვესტიციის პირობები",
                "სასტუმროს ნომრის ფასი",
                "როგორ ვიღებ შემოსავალს და როგორ ითვლება იგი წლიურად?",
            ]
            return {
                "messages": [AIMessage(content="🤔 რა გაინტერესებთ კონკრეტულად? აირჩიეთ პასუხი:")],
                "quick_replies": quick_buttons(investment_buttons)
            }
        elif msg == "როგორ ვიღებ შემოსავალს და როგორ ითვლება იგი წლიურად?":
            project_buttons = [
                "დიახ",
                "არა"
            ]
            return {
                "messages": [AIMessage(
                    content="💳 შემოსავალს იღებთ თქვენ მიერ შეძენილი სასტუმრო ნომრის გაქირავებით. შემოსავალი პროპორციულად იყოფა, უნიკალურ მოდელზე დაფუძნებით, ყველა ინვესტორს შორის. $150,000-ის გადახდის შემთხვევაში წლიური შემოსავალი შეადგენს $35,000-ს და მმართველი კომპანია საკუთარ თავზე აიღებს საოპერაციო ასპექტებს.უნიკალური მოდელი გარანტიას იძლევა, რომ ყველა ინვესტორი თანაბარ მოგებას მიიღებს სასტუმროს საერთო შემოსავლიდან. გაქვს დამატებითი კითხვები?"
                )],
                "quick_replies": quick_buttons(project_buttons)
            }

        elif msg == "სასტუმროს ნომრის ფასი":
            project_buttons = [
                "დიახ",
                "არა"
            ]
            return {
                "messages": [AIMessage(
                    content="💰 Radisson Blu-ს სასტუმროს ნომრის ღირებულება იწყება $150,000 და იზრდება მაღლა, რაც მეტი წვესტიციასა და უფრო მაღალ შემოსავალს გთავაზობთ. გაქვს დამატებითი კითხვები?"
                )],
                "quick_replies": quick_buttons(project_buttons)
            }

        elif msg == "ინვესტიციის პირობები":
            project_buttons = [
                "დიახ",
                "არა"
            ]
            return {
                "messages": [AIMessage(
                    content="🎇 ჩვენ გთავაზობთ უნიკალურ შესაძლებლობას, შეიძინოთ ნომერი სასტუმრო Radisson Blu-do $150,000-ად. ეს არის ინვესტიცია, რომელსაც შეუძლია მოიტანოს ყოველწლიურად $35,000 მოგება, რაც უზრუნველყოფს მაღალ შემოსავალს, დაახლოებით წლიურ 24%-ს. გაქვს დამატებითი კითხვები?"
                )],
                "quick_replies": quick_buttons(project_buttons)
            }


        else:
            system_prompt = """You are the chatbot for Orbi Group, a construction and development company. 
                    Always be professional and use emojis appropriately. For specific questions about project details, 
                    use the retrieve_documents function to ensure accuracy.If user give phone number respond: "🧐 Before our team gets in touch with you, is there anything else you are interested in?" 
                    
                    Be polite and use polite emojis for greetings , goodbye, or thankful interactions.
                    
                    1. Central Park Towers is a 5-star integrated resort and hotel complex located on Alexander Kazbegi Avenue, near Central Park in Tbilisi, Georgia. It is managed by Radisson Blu and features a range of international brands in hospitality, dining, shopping, and entertainment.
                    2. Central Park Towers includes:
                    7 international brand restaurants
                    Georgia’s first luxury shopping mall, managed by Harvey Nichols
                    The region's largest multifunctional event hall for 2,500 people
                    The biggest casino in Georgia, operated by a Macau-based company
                    Premium-class spa and wellness facilities managed by Spa Soul
                    Ample parking and modern office spaces
                    3. When will Central Park Towers be completed?
                    Construction of Central Park Towers is actively progressing, with the complex scheduled for completion by December 2025. This includes the full finishing and equipping of hotel rooms and other facilities.(Georgian Translation: Central Park Towers-ი უკვე აქტიური შენების პროცესშია, რომელიც 2025 წლის დეკემბერში დასრულდება. რაც გულისხმობს სასტუმროს ნომრების და სხვა ობიექტების მთლიანად კეთილმოწყობას.)
                    4. What investment opportunities does Central Park Towers offer?
                    We offer the unique opportunity to purchase a hotel room in the Radisson Blu hotel for $150,000. This investment is expected to generate an annual income of $35,000, providing a high return of approximately 24% per year.
                    5. How is the income generated from my investment and how does profit-sharing work?
                    The income is generated by renting out your purchased hotel room through the Radisson Blu hotel. The profits are shared among all investors equally, based on a unique profit-sharing model. Annual income from a $150,000 room purchase is expected to be $35,000, with the management taking care of all operational aspects. The profit-sharing model ensures all investors benefit equally from the hotel's overall performance.
                    6. How is the hotel room managed, and what are the associated costs?
                    Radisson Blu manages all hotel rooms within the complex. The management fee is 15% of the turnover, and investors are exempt from utility and fixed operational costs. The rooms come fully furnished and equipped, ensuring a hassle-free experience for investors.
                    7. How secure is my investment?
                    Your investment is secured by a preliminary purchase agreement, which can be signed online or in person. Ownership rights are transferred upon full payment, and the agreement ensures full legal protection. Leading global audit firms, such as Deloitte and Ernst & Young, will audit the project, guaranteeing transparency and trust.
                    8. Why is Georgia a secure and attractive country for investment?
                    Return exact answer: Georgia offers a stable and growing economy, driven by tourism, real estate, and foreign investments. With its strategic location at the crossroads of Europe and Asia, Georgia has developed a business-friendly environment, including low taxes and simplified regulations. The country boasts a rich cultural heritage, stunning landscapes, and a booming tourism sector. As a candidate for EU membership and part of the Schengen Zone, Georgia provides investors with long-term growth potential and increased global connectivity.
                    9. How can I purchase a hotel room in Central Park Towers?
                    Purchasing a hotel room is simple. You can either pay the full amount upfront or choose one of our flexible payment plans. The internal instalment plan requires a 35% down payment, with the remaining balance paid in monthly instalments during construction. Alternatively, a bank loan can spread payments over 60 months with no early repayment fees.
                    10. Will I be eligible for a Georgian residence permit if I purchase a hotel room?
                    Yes, purchasing a hotel room in Central Park Towers qualifies you for a Georgian residence permit. This offers you the opportunity to live and work in Georgia. Additionally, Georgia is a candidate for EU membership and member of the Schengen Zone.
                    11. What happens if I want to sell my hotel room later?
                    You are free to sell your hotel room at any time after purchase. Given the high demand and unique location, the value of your property is expected to appreciate significantly, allowing for a profitable resale.
                    
                    Note:For Every queries respond user that If you have other questions, please choose how I can help you: 
                    Remember: Answer in whichever language the question is asked. 
                    """
            m = []
            m.append(SystemMessage(content=system_prompt))
            m.extend(messages)
            model = ChatOpenAI(temperature=0, model="gpt-4o-mini", api_key=settings.openai_api_key)
            model = model.bind_tools(tools)
            response = await model.ainvoke(m)

            # await messenger_client.send_text_message(
            #     sender_id,
            #     response.content,
            # )
            async def send_carousel():
                await asyncio.sleep(1.5)
                await messenger_client.send_generic_template(sender_id, carousel_elements)

            return_value = {
                "messages": [AIMessage(content=response.content)],
                "suppress_response": False
            }

            asyncio.create_task(send_carousel())
            return return_value


class RewriteNode:

    async def __call__(self, state: AgentState, config):
        """
            Transform the query to produce a better question.

            Args:
                state (messages): The current state

            Returns:
                dict: The updated state with re-phrased question
            """

        logging.info("---TRANSFORM QUERY---")
        messages = state.messages
        question = messages[-1].content

        msg = [
            HumanMessage(
                content=f""" \n 
            Look at the input and try to reason about the underlying semantic intent / meaning. \n 
            Here is the initial question:
            \n ------- \n
            {question} 
            \n ------- \n
            Formulate an improved question: """,
            )
        ]

        # Grader

        model = ChatOpenAI(temperature=0, model="gpt-4o-mini", api_key=settings.openai_api_key)

        response = await model.ainvoke(msg)

        return {"messages": [response]}


class GenerateNode:

    async def __call__(self, state: AgentState, config):
        """
            Generate answer

            Args:
                state (messages): The current state

            Returns:
                 dict: The updated state with re-phrased question
            """
        logging.info("---GENERATE---")
        messages = state.messages
        question = messages[0].content
        last_message = messages[-1]

        docs = last_message.content

        # Prompt
        template = """Use the following pieces of context to answer the question at the end.
        If you don't know the answer(context is not enough), just say: 🔎 დეტალური ინფორმაციის მისაღებად მოგვწერეთ საკონტაქტო ტელ.ნომერი (WhatsApp/viber) ჩვენი გაყიდვების მენეჯერი დაგიკავშირდებათ  და უპასუხებს ყველა თქვენს შეკითხვას
        Keep the answer concisely. Target only users last question and answer to directly provide answer. Use emojis as needed.
        Never make assumption, only use provided context.
        ask for info as needed you can ask questions to user to provide better answers.
        
        {context}

        Conversation: {conversation}

        Helpful Answer:"""

        prompt = PromptTemplate.from_template(template)

        # LLM
        llm = ChatOpenAI(temperature=0,
                         api_key=settings.openai_api_key,
                         model='gpt-4o-mini')

        # Post-processing
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        # Chain
        rag_chain = prompt | llm | StrOutputParser()

        # Run
        response = await rag_chain.ainvoke({"context": docs, "conversation": state.messages})

        return {"messages": [AIMessage(content=response)], "rewrite_attempts": 0}
