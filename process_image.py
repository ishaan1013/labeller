import base64


def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def process_image(client, image_path):

    base64_image = encode_image_to_base64(image_path)

    # completion = client.beta.chat.completions.parse(
    #     messages=[{
    #         "role": "user",
    #         "content": [{
    #             "type": "text",
    #             "text": "This image is a screenshot of a website. All clickable elements (such as links and buttons) are highlighted with a red border. Please describe each highlighted element in a few words, focusing on its likely function based on its appearance and context."
    #         }, {
    #             "type": "image_url",
    #             "image_url": {
    #                 "url": f"data:image/jpeg;base64,{base64_image}"
    #             }
    #         }]
    #     }],
    #     model="gpt-4o-2024-08-06",
    #     response_format=,
    # )

    completion = client.chat.completions.create(
        messages=[{
            "role": "user",
            "content": [{
                "type": "text",
                "text": "This image is a screenshot of a website. All clickable elements (such as links and buttons) are highlighted with a red border. Please describe each highlighted element in a few words, focusing on its likely function based on its appearance and context."
            }, {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            }]
        }],
        model="gpt-4o",
    )

    # return completion.choices[0].message.parsed
    return completion.choices[0].message.content
