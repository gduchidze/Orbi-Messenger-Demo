import asyncio
import logging

from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from langchain_core.messages import HumanMessage

from app.agent.workflow import AgentWorkflow
from app.config import settings
from app.messenger import messenger_client
from app.models import MessengerWebhookPayload

app = FastAPI()

#
workflow = AgentWorkflow()
agent = workflow.compile()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/messenger/webhook")
async def messenger_verify(mode: str = Query(None, alias="hub.mode"),
                           token: str = Query(None, alias="hub.verify_token"),
                           challenge: str = Query(None, alias="hub.challenge")):
    #
    if mode == "subscribe" and challenge:

        #
        if token != settings.messenger_verify_token:
            logging.error('Verification token mismatch - %d', 403)
            raise HTTPException(status_code=403, detail="Verification token mismatch")

        #
        logging.info('Verification successful - %d', 200)
        return JSONResponse(content=int(challenge), status_code=200)

    html_content = """
    <!DOCTYPE html>
    <html lang="es">
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Verificación de Token</title>
        <style>
          body {
            font-family: Arial, sans-serif;
            margin: 20px;
          }
          .container {
            max-width: 600px;
            margin: auto;
            padding: 20px;
            border: 1px solid #ccc;
            border-radius: 5px;
            background-color: #f9f9f9;
          }
          h1 {
            text-align: center;
          }
          p {
            text-align: center;
          }
        </style>
      </head>
      <body>
        <div class="container">
          <h1>Hello, World!</h1>
          <p>This is the endpoint to verify the token 🔐🔗</p>
        </div>
      </body>
    </html>
    """

    #
    logging.warning('This endpoint is to verify token - %d', 200)
    return HTMLResponse(content=html_content, status_code=200)


@app.post("/messenger/webhook")
async def messenger_webhook(payload: MessengerWebhookPayload):
    logging.info("====== NEW WEBHOOK REQUEST ======")

    try:
        if payload.object != "page":
            logging.info(f"Ignoring non-page object: {payload.object}")
            return {"status": "not handled"}

        for entry in payload.entry:
            for event in entry.messaging:
                sender_id = event.sender.id
                logging.info(f"Processing event for sender: {sender_id}")
                logging.info(f"Full event data: {event}")  # დავლოგოთ მთლიანი ივენთი

                # შეამოწმეთ postback-ის არსებობა
                postback = getattr(event, 'postback', None)
                if postback and hasattr(postback, 'payload'):
                    message_type = "postback"
                    message_content = postback.payload
                    logging.info(f"POSTBACK received: {message_content}")

                # თუ postback არ არის, შეამოწმეთ მესიჯი
                elif hasattr(event, 'message') and hasattr(event.message, 'text'):
                    message_type = "message"
                    message_content = event.message.text
                    logging.info(f"MESSAGE received: {message_content}")

                else:
                    logging.warning("Unknown event type")
                    logging.warning(f"Event structure: {vars(event)}")  # დავლოგოთ ივენთის სტრუქტურა
                    continue

                # დამუშავების პროცესი
                try:
                    logging.info(f"Preparing to send to agent: Type={message_type}, Content={message_content}")

                    messages = [HumanMessage(content=message_content)]
                    config = {
                        "configurable": {
                            "thread_id": sender_id,
                            "message_type": message_type
                        }
                    }

                    logging.info("Calling agent.ainvoke")
                    response = await agent.ainvoke(input={"messages": messages}, config=config)
                    logging.info(f"Agent response received: {response}")

                    if response:
                        if not response.get('suppress_response', False):
                            message_text = response.get('messages', [])[-1].content
                            quick_replies = response.get('quick_replies')

                            # თუ არის კარუსელის ელემენტები
                            carousel_elements = response.get('carousel_elements')
                            if carousel_elements:
                                logging.info("Sending generic template")
                                await messenger_client.send_generic_template(sender_id, carousel_elements)
                            else:
                                logging.info(f"Sending message: {message_text}")
                                await messenger_client.send_text_message(
                                    sender_id,
                                    message_text,
                                    quick_replies=quick_replies
                                )
                    else:
                        logging.warning("Empty response from agent")

                except Exception as e:
                    logging.error(f"Error processing message: {str(e)}", exc_info=True)
                    await messenger_client.send_text_message(
                        sender_id,
                        "მოითმინეთ ჩვენი წარმომადგენლები აუცილებლად დაგიკავშირდებიან."
                    )

    except Exception as e:
        logging.error(f"Error in webhook handler: {str(e)}", exc_info=True)
        return {"status": "error", "message": str(e)}

    logging.info("====== WEBHOOK REQUEST COMPLETED ======")
    return {"status": "success"}
