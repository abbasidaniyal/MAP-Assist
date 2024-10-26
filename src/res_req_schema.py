def get_status_payload(req, context):
    if req.status_code >= 400:
        payload = {
            "status": "error"
        }
    else:
        response = req.json()
        payload = {
            "status": "success",
            # "res": response # TODO
            # "res": response['res'],
            # "context": response['context'],
            "res": response['milliseconds_since_epoch'],
            "context": context,
            # "res_type": None
        }
    return payload
