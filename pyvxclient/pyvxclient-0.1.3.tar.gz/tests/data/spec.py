spec = {
    "basePath": "/api/v1/",
    "definitions": {
        "Customer": {
            "properties": {
                "b_address": {
                    "type": "string"
                },
                "b_city": {
                    "type": "string"
                },
                "b_full_name": {
                    "type": "string"
                },
                "b_postal_code": {
                    "type": "string"
                },
                "c_o": {
                    "type": "string"
                },
                "city": {
                    "type": "string"
                },
                "company_name": {
                    "type": "string"
                },
                "country": {
                    "type": "string"
                },
                "country_code": {
                    "type": "string"
                },
                "created": {
                    "type": "string"
                },
                "customer_number": {
                    "type": "string"
                },
                "customer_type": {
                    "type": "string"
                },
                "email": {
                    "type": "string"
                },
                "first_name": {
                    "type": "string"
                },
                "id": {
                    "type": "string"
                },
                "language": {
                    "type": "string"
                },
                "last_name": {
                    "type": "string"
                },
                "mobile_number": {
                    "type": "string"
                },
                "phone_number": {
                    "type": "string"
                },
                "postal_code": {
                    "type": "string"
                },
                "province": {
                    "type": "string"
                },
                "reference": {
                    "type": "string"
                },
                "ssn": {
                    "type": "string"
                },
                "street_address": {
                    "type": "string"
                },
                "updated": {
                    "type": "string"
                },
                "username": {
                    "type": "string"
                }
            },
            "type": "object"
        },
        "HTTPError4XX": {
            "properties": {
                "message": {
                    "type": "string"
                }
            },
            "required": [
                "message"
            ],
            "type": "object"
        },
        "Object": {
            "properties": {
                "active_from": {
                    "type": "string"
                },
                "apartment_number": {
                    "type": "string"
                },
                "build_status": {
                    "type": "string"
                },
                "building": {
                    "type": "string"
                },
                "city": {
                    "type": "string"
                },
                "class_code": {
                    "type": "string"
                },
                "created": {
                    "type": "string"
                },
                "homedrop_price": {
                    "type": "string"
                },
                "homedrop_status": {
                    "type": "string"
                },
                "id": {
                    "type": "string"
                },
                "include_in_sdr": {
                    "enum": [
                        [
                            False,
                            True
                        ]
                    ],
                    "type": "string"
                },
                "latitude": {
                    "type": "string"
                },
                "longitude": {
                    "type": "string"
                },
                "manual_provisioning": {
                    "enum": [
                        [
                            "u'Yes'",
                            "u'No'"
                        ]
                    ],
                    "type": "string"
                },
                "network": {
                    "type": "string"
                },
                "network_operator": {
                    "type": "string"
                },
                "note": {
                    "type": "string"
                },
                "object_group": {
                    "type": "string"
                },
                "object_number": {
                    "type": "string"
                },
                "object_type": {
                    "type": "string"
                },
                "old_latitude": {
                    "type": "string"
                },
                "old_longitude": {
                    "type": "string"
                },
                "organization": {
                    "type": "string"
                },
                "port": {
                    "type": "string"
                },
                "postal_code": {
                    "type": "string"
                },
                "province": {
                    "type": "string"
                },
                "provisioning_status": {
                    "enum": [
                        [
                            "u'Configured'",
                            "u'Unknown'",
                            "u'Configuration error'",
                            "u'Awaiting configuration'",
                            "u'No configuration requested'"
                        ]
                    ],
                    "type": "string"
                },
                "public_note": {
                    "type": "string"
                },
                "status": {
                    "enum": [
                        [
                            "u'Not deliverable'",
                            "u'In deployment'",
                            "u'Deliverable'"
                        ]
                    ],
                    "type": "string"
                },
                "street": {
                    "type": "string"
                },
                "street_number": {
                    "type": "string"
                },
                "survey_result": {
                    "type": "string"
                },
                "updated": {
                    "type": "string"
                }
            },
            "type": "object"
        },
        "Order": {
            "properties": {
                "activated_date": {
                    "type": "string"
                },
                "cancellation_date": {
                    "type": "string"
                },
                "created": {
                    "type": "string"
                },
                "customer": {
                    "type": "string"
                },
                "from_date": {
                    "type": "string"
                },
                "id": {
                    "type": "string"
                },
                "is_paid": {
                    "type": "string"
                },
                "network_operator": {
                    "type": "string"
                },
                "object": {
                    "type": "string"
                },
                "operator_order_number": {
                    "type": "string"
                },
                "order_number": {
                    "type": "string"
                },
                "parent": {
                    "type": "string"
                },
                "price": {
                    "type": "string"
                },
                "provider_order_number": {
                    "type": "string"
                },
                "reference": {
                    "type": "string"
                },
                "sales_lead": {
                    "type": "string"
                },
                "service": {
                    "type": "string"
                },
                "service_provider": {
                    "type": "string"
                },
                "shelved_date": {
                    "type": "string"
                },
                "state": {
                    "enum": [
                        [
                            "u'Approve'",
                            "u'Unshelved'",
                            "u'Force termination'",
                            "u'Cancelled'",
                            "u'Awaiting activation'",
                            "u'Active'",
                            "u'Shelved'"
                        ]
                    ],
                    "type": "string"
                },
                "status": {
                    "type": "string"
                },
                "terminated_date": {
                    "type": "string"
                },
                "updated": {
                    "type": "string"
                }
            },
            "type": "object"
        },
        "Place": {
            "properties": {
                "accept_survey_message": {
                    "type": "string"
                },
                "cancel_message": {
                    "type": "string"
                },
                "city": {
                    "type": "string"
                },
                "customer_type": {
                    "type": "string"
                },
                "earlystart_message": {
                    "type": "string"
                },
                "latitude": {
                    "type": "string"
                },
                "longitude": {
                    "type": "string"
                },
                "n_services": {
                    "type": "integer"
                },
                "network_operator": {
                    "type": "string"
                },
                "object": {
                    "properties": {
                        "build_status": {
                            "enum": [
                                [
                                    "connected",
                                    "passed",
                                    "in construction",
                                    "planned near",
                                    "planned",
                                    "interest",
                                    "dismissed"
                                ]
                            ],
                            "type": "string"
                        },
                        "id": {
                            "type": "string"
                        },
                        "object_group": {
                            "type": "string"
                        },
                        "object_number": {
                            "type": "string"
                        }
                    },
                    "type": "object"
                },
                "postal_code": {
                    "type": "string"
                },
                "progress": {
                    "properties": {
                        "connected": {
                            "type": "boolean"
                        },
                        "connection_ready": {
                            "type": "boolean"
                        },
                        "downpayment": {
                            "type": "boolean"
                        },
                        "installation_appointment": {
                            "type": "boolean"
                        },
                        "order_confirmation": {
                            "type": "boolean"
                        }
                    },
                    "type": "object"
                },
                "province": {
                    "type": "string"
                },
                "reject_survey_message": {
                    "type": "string"
                },
                "status": {
                    "type": "string"
                },
                "street": {
                    "type": "string"
                },
                "street_number": {
                    "type": "string"
                },
                "workflow": {
                    "properties": {
                        "business_key": {
                            "type": "string"
                        },
                        "definition_key": {
                            "type": "string"
                        },
                        "version_tag": {
                            "type": "string"
                        }
                    },
                    "type": "object"
                }
            },
            "type": "object"
        },
        "Service": {
            "properties": {
                "auto_approve_move": {
                    "type": "string"
                },
                "auto_approve_new": {
                    "type": "string"
                },
                "bind_time": {
                    "type": "string"
                },
                "created": {
                    "type": "string"
                },
                "definition": {
                    "type": "string"
                },
                "description": {
                    "type": "string"
                },
                "fees": {
                    "type": "string"
                },
                "from_date": {
                    "type": "string"
                },
                "id": {
                    "type": "string"
                },
                "name": {
                    "type": "string"
                },
                "notice_time": {
                    "type": "string"
                },
                "object_groups": {
                    "type": "string"
                },
                "price": {
                    "type": "string"
                },
                "referral_url": {
                    "type": "string"
                },
                "service_id": {
                    "type": "string"
                },
                "service_provider": {
                    "type": "string"
                },
                "service_provider_name": {
                    "type": "string"
                },
                "service_type": {
                    "type": "string"
                },
                "status": {
                    "enum": [
                        [
                            "u'Editing'",
                            "u'Unknown (3)'",
                            "u'Unknown (2)'",
                            "u'Orderable'",
                            "u'Obsolete'",
                            "u'Editing'"
                        ]
                    ],
                    "type": "string"
                },
                "to_date": {
                    "type": "string"
                },
                "updated": {
                    "type": "string"
                },
                "version": {
                    "type": "string"
                },
                "visibility": {
                    "enum": [
                        [
                            True,
                            False
                        ]
                    ],
                    "type": "string"
                },
                "visibility_type": {
                    "type": "string"
                },
                "vlans": {
                    "type": "string"
                }
            },
            "type": "object"
        }
    },
    "host": "vxapitest-demo.vx.se",
    "info": {
        "description": "VNAPI exposes business and provisioning resources available in the Ventura Next backend",
        "title": "VNAPI",
        "version": "v1919.0.2"
    },
    "paths": {
        "/api": {
            "get": {
                "description": "Return API version and release, server time",
                "operationId": "getApi",
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Return the correct information",
                        "schema": {
                            "properties": {
                                "currency": {
                                    "type": "string"
                                },
                                "release": {
                                    "type": "string"
                                },
                                "request_client_ip": {
                                    "type": "string"
                                },
                                "request_source_ip": {
                                    "type": "string"
                                },
                                "settings": {
                                    "type": "object"
                                },
                                "utc_time": {
                                    "type": "string"
                                },
                                "version": {
                                    "type": "string"
                                }
                            },
                            "type": "object"
                        }
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get list of information regarding the server and the API",
                "tags": [
                    "api"
                ]
            }
        },
        "/api/address": {
            "get": {
                "description": "Get address geolocation",
                "operationId": "getApiAddress",
                "parameters": [
                    {
                        "description": "Address",
                        "in": "query",
                        "name": "address",
                        "type": "string"
                    },
                    {
                        "description": "Latitude",
                        "in": "query",
                        "name": "latitude",
                        "type": "number"
                    },
                    {
                        "description": "Longitude",
                        "in": "query",
                        "name": "longitude",
                        "type": "number"
                    },
                    {
                        "description": "Network Operator",
                        "in": "query",
                        "name": "network_operator",
                        "type": "string"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "log list",
                        "schema": {
                            "properties": {
                                "address": {
                                    "items": {
                                        "properties": {
                                            "address": {
                                                "properties": {
                                                    "city": {
                                                        "type": "string"
                                                    },
                                                    "country": {
                                                        "type": "string"
                                                    },
                                                    "postal_code": {
                                                        "type": "string"
                                                    },
                                                    "province": {
                                                        "type": "string"
                                                    },
                                                    "street": {
                                                        "type": "string"
                                                    }
                                                },
                                                "type": "object"
                                            },
                                            "formatted_address": {
                                                "type": "string"
                                            },
                                            "position": {
                                                "properties": {
                                                    "coordinates": {
                                                        "items": {
                                                            "type": "number"
                                                        },
                                                        "type": "array"
                                                    },
                                                    "type": {
                                                        "type": "string"
                                                    }
                                                },
                                                "type": "object"
                                            },
                                            "zone": {
                                                "properties": {
                                                    "id": {
                                                        "type": "string"
                                                    },
                                                    "name": {
                                                        "type": "string"
                                                    },
                                                    "object_group": {
                                                        "type": "string"
                                                    },
                                                    "status": {
                                                        "type": "string"
                                                    }
                                                },
                                                "type": "object"
                                            }
                                        },
                                        "type": "object"
                                    },
                                    "type": "array"
                                }
                            },
                            "type": "object"
                        }
                    },
                    "410": {
                        "description": "address or latitude and longitude are missing"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get address geolocation",
                "tags": [
                    "api"
                ]
            }
        },
        "/api/api_key": {
            "get": {
                "description": "Generate a temporary api_key that will be used for accessing the API",
                "operationId": "getApiKey",
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "return the new api_key and the expire",
                        "schema": {
                            "properties": {
                                "api_key": {
                                    "type": "string"
                                },
                                "expires": {
                                    "format": "dateTime",
                                    "type": "string"
                                }
                            },
                            "type": "object"
                        }
                    }
                },
                "security": [
                    {
                        "basicAuth": []
                    }
                ],
                "summary": "Generate an api_key",
                "tags": [
                    "api"
                ]
            }
        },
        "/api/blacklist": {
            "get": {
                "description": "Returns a list of api logs. The log is currently only available for admin.s",
                "operationId": "getApiBlacklist",
                "parameters": [
                    {
                        "default": 1,
                        "description": "page requested",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 1000 entries is the maximum allowed value",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "collectionFormat": "csv",
                        "default": [
                            "id"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "by default all the fields are returned but if a subset is required, list all the ones that should be included in the response",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "fields",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "log list",
                        "schema": {
                            "items": {
                                "properties": {
                                    "client_ip": {
                                        "type": "string"
                                    },
                                    "created": {
                                        "type": "string"
                                    },
                                    "id": {
                                        "type": "string"
                                    },
                                    "interval": {
                                        "type": "string"
                                    },
                                    "num_requests": {
                                        "type": "string"
                                    },
                                    "state": {
                                        "type": "string"
                                    },
                                    "updated": {
                                        "type": "string"
                                    },
                                    "user": {
                                        "type": "string"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "404": {
                        "description": "no log records found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get a list of api logs",
                "tags": [
                    "api"
                ]
            }
        },
        "/api/email": {
            "post": {
                "description": "Send a new email.",
                "operationId": "postEmail",
                "parameters": [
                    {
                        "description": "email to be sent",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "body": {
                                    "type": "string"
                                },
                                "context": {
                                    "type": "string"
                                },
                                "from_email": {
                                    "type": "string"
                                },
                                "subject": {
                                    "type": "string"
                                },
                                "template": {
                                    "type": "string"
                                },
                                "to_email": {
                                    "type": "string"
                                }
                            },
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "201": {
                        "description": "email sent"
                    },
                    "400": {
                        "description": "bad request or field values not valid"
                    },
                    "401": {
                        "description": "Error sending email"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Send a new email.",
                "tags": [
                    "api"
                ]
            }
        },
        "/api/language": {
            "delete": {
                "description": "Delete a Language",
                "operationId": "deleteLanguage",
                "parameters": [
                    {
                        "description": "deleted language",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "id": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "id"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Language has been deleted"
                    },
                    "403": {
                        "description": "permission issue"
                    },
                    "404": {
                        "description": "language not found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Delete a Language",
                "tags": [
                    "api"
                ]
            },
            "get": {
                "description": "Returns a list of supported languages",
                "operationId": "getLanguage",
                "parameters": [
                    {
                        "default": 1,
                        "description": "page requested",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 1000 entries is the maximum allowed value",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "collectionFormat": "csv",
                        "default": [
                            "id"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "by default all the fields are returned but if a subset is required, list all the ones that should be included in the response",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "fields",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "language list",
                        "schema": {
                            "items": {
                                "properties": {
                                    "created": {
                                        "type": "string"
                                    },
                                    "id": {
                                        "type": "string"
                                    },
                                    "name": {
                                        "type": "string"
                                    },
                                    "updated": {
                                        "type": "string"
                                    },
                                    "visibility": {
                                        "type": "string"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "404": {
                        "description": "no language records found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get a list of supported languages",
                "tags": [
                    "api"
                ]
            }
        },
        "/api/log": {
            "get": {
                "description": "Returns a list of api logs. The log is currently only available for admin.s",
                "operationId": "getApiLog",
                "parameters": [
                    {
                        "default": 1,
                        "description": "page requested",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 1000 entries is the maximum allowed value",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "collectionFormat": "csv",
                        "default": [
                            "id"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "by default all the fields are returned but if a subset is required, list all the ones that should be included in the response",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "fields",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "log list",
                        "schema": {
                            "items": {
                                "properties": {
                                    "args": {
                                        "type": "string"
                                    },
                                    "client_ip": {
                                        "type": "string"
                                    },
                                    "customer": {
                                        "type": "string"
                                    },
                                    "customer_number": {
                                        "type": "string"
                                    },
                                    "duration": {
                                        "type": "string"
                                    },
                                    "host": {
                                        "type": "string"
                                    },
                                    "id": {
                                        "type": "string"
                                    },
                                    "method": {
                                        "type": "string"
                                    },
                                    "network_operator": {
                                        "type": "string"
                                    },
                                    "object": {
                                        "type": "string"
                                    },
                                    "object_number": {
                                        "type": "string"
                                    },
                                    "order": {
                                        "type": "string"
                                    },
                                    "order_number": {
                                        "type": "string"
                                    },
                                    "resource": {
                                        "type": "string"
                                    },
                                    "response": {
                                        "type": "string"
                                    },
                                    "service": {
                                        "type": "string"
                                    },
                                    "service_provider": {
                                        "type": "string"
                                    },
                                    "start": {
                                        "type": "string"
                                    },
                                    "status_code": {
                                        "type": "string"
                                    },
                                    "timestamp": {
                                        "type": "string"
                                    },
                                    "user": {
                                        "type": "string"
                                    },
                                    "vx_for_client_ip": {
                                        "type": "string"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "404": {
                        "description": "no log records found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get a list of api logs",
                "tags": [
                    "api"
                ]
            }
        },
        "/api/logout": {
            "get": {
                "description": "Remove api_key",
                "operationId": "getApiLogout",
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "succesfull logout"
                    },
                    "404": {
                        "description": "api key not found"
                    }
                },
                "summary": "Logout",
                "tags": [
                    "api"
                ]
            }
        },
        "/api/map": {
            "get": {
                "description": "Get maps",
                "operationId": "getApiMap",
                "parameters": [
                    {
                        "description": "latitude",
                        "in": "query",
                        "name": "latitude",
                        "type": "number"
                    },
                    {
                        "description": "longitude",
                        "in": "query",
                        "name": "longitude",
                        "type": "number"
                    },
                    {
                        "description": "map height in pixels (default 300)",
                        "in": "query",
                        "name": "height",
                        "type": "integer"
                    },
                    {
                        "description": "map width in pixels (default 600)",
                        "in": "query",
                        "name": "width",
                        "type": "integer"
                    },
                    {
                        "description": "map zoom (default 16)",
                        "in": "query",
                        "name": "zoom",
                        "type": "integer"
                    },
                    {
                        "description": "map markers format (default color:red)",
                        "in": "query",
                        "name": "markers",
                        "type": "string"
                    },
                    {
                        "description": "map style. Multile style must be separated by ; (default no style)",
                        "in": "query",
                        "name": "style",
                        "type": "string"
                    }
                ],
                "produces": [
                    "application/png"
                ],
                "responses": {
                    "200": {
                        "description": "Map image"
                    },
                    "410": {
                        "description": "Impossible to get the map"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get maps",
                "tags": [
                    "api"
                ]
            }
        },
        "/api/my_profile": {
            "get": {
                "description": "Return always the role of the profile accessing the api plus information that depends on the profile itself",
                "operationId": "getApiMyProfile",
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "return my profile information",
                        "schema": {
                            "properties": {
                                "id": {
                                    "type": "string"
                                },
                                "name": {
                                    "type": "string"
                                },
                                "role": {
                                    "type": "string"
                                }
                            },
                            "type": "object"
                        }
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get api user profile",
                "tags": [
                    "api"
                ]
            }
        },
        "/api/query": {
            "delete": {
                "description": "Delete the query with a specific id, if exists",
                "parameters": [
                    {
                        "description": "updated query",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "action": {
                                    "type": "string"
                                },
                                "action_args": {
                                    "type": "string"
                                },
                                "id": {
                                    "type": "string"
                                },
                                "last_error": {
                                    "type": "string"
                                },
                                "last_result": {
                                    "type": "string"
                                },
                                "last_run": {
                                    "type": "string"
                                },
                                "resource": {
                                    "type": "string"
                                },
                                "run_count": {
                                    "type": "string"
                                },
                                "user": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "resource",
                                "last_error",
                                "last_run",
                                "last_result",
                                "user",
                                "run_count",
                                "action",
                                "id",
                                "action_args"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "query has been deleted"
                    },
                    "400": {
                        "description": "the id supplier is not a valid GUID"
                    },
                    "404": {
                        "description": "query was not found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Delete a query",
                "tags": [
                    "api"
                ]
            },
            "get": {
                "description": "Returns a list of queries.",
                "operationId": "getApiQuery",
                "parameters": [
                    {
                        "default": 1,
                        "description": "page requested",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 1000 entries is the maximum allowed value",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "collectionFormat": "csv",
                        "default": [
                            "id"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "by default all the fields are returned but if a subset is required, list all the ones that should be included in the response",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "fields",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "queries list",
                        "schema": {
                            "items": {
                                "properties": {
                                    "action": {
                                        "type": "string"
                                    },
                                    "action_args": {
                                        "type": "string"
                                    },
                                    "id": {
                                        "type": "string"
                                    },
                                    "last_error": {
                                        "type": "string"
                                    },
                                    "last_result": {
                                        "type": "string"
                                    },
                                    "last_run": {
                                        "type": "string"
                                    },
                                    "resource": {
                                        "type": "string"
                                    },
                                    "run_count": {
                                        "type": "string"
                                    },
                                    "user": {
                                        "type": "string"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "404": {
                        "description": "no queries records found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get a list of queries",
                "tags": [
                    "api"
                ]
            },
            "post": {
                "description": "Create a new query. The query with be executed at resular intervals and if there is a change<br/>an action will done. The actions currently supported are EMAIL, http(s) PUT and http(s) POST.<br/>Action args depends from action.",
                "parameters": [
                    {
                        "description": "query to be added",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "action": {
                                    "type": "string"
                                },
                                "action_args": {
                                    "type": "string"
                                },
                                "resource": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "resource",
                                "action",
                                "action_args"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "201": {
                        "description": "query created"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Create a new query",
                "tags": [
                    "api"
                ]
            },
            "put": {
                "description": "Update the query with a specific id, if exists",
                "parameters": [
                    {
                        "description": "updated query",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "action": {
                                    "type": "string"
                                },
                                "action_args": {
                                    "type": "string"
                                },
                                "id": {
                                    "type": "string"
                                },
                                "resource": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "id"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "query has been updated"
                    },
                    "400": {
                        "description": "the id supplier is not a valid GUID"
                    },
                    "404": {
                        "description": "query was not found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Update a query",
                "tags": [
                    "api"
                ]
            }
        },
        "/api/synchronization": {
            "get": {
                "description": "Returns a list of information about the synchronization of some resources",
                "operationId": "getApiSynchronization",
                "parameters": [
                    {
                        "default": 1,
                        "description": "page requested",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 1000 entries is the maximum allowed value",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "collectionFormat": "csv",
                        "default": [
                            "id"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "by default all the fields are returned but if a subset is required, list all the ones that should be included in the response",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "fields",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "log list",
                        "schema": {
                            "items": {
                                "properties": {
                                    "daily_time": {
                                        "type": "string"
                                    },
                                    "error": {
                                        "type": "string"
                                    },
                                    "id": {
                                        "type": "string"
                                    },
                                    "interval": {
                                        "type": "string"
                                    },
                                    "last_duration": {
                                        "type": "string"
                                    },
                                    "last_start": {
                                        "type": "string"
                                    },
                                    "last_stop": {
                                        "type": "string"
                                    },
                                    "resource": {
                                        "type": "string"
                                    },
                                    "result": {
                                        "type": "string"
                                    },
                                    "status": {
                                        "type": "string"
                                    },
                                    "strategy": {
                                        "type": "string"
                                    },
                                    "sync_type": {
                                        "type": "string"
                                    },
                                    "updated": {
                                        "type": "string"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "404": {
                        "description": "no log records found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get a list synchronization information",
                "tags": [
                    "api"
                ]
            }
        },
        "/api/template": {
            "delete": {
                "description": "Delete a template",
                "parameters": [
                    {
                        "description": "deleted a template",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "id": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "id"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "template has been deleted"
                    },
                    "403": {
                        "description": "permission issue"
                    },
                    "404": {
                        "description": "template not found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Delete a template",
                "tags": [
                    "api"
                ]
            },
            "get": {
                "description": "Returns a list of templates. Template types can be:<br/>- \"sales_lead_confirm\" used to require a sales lead confirmation (variables to be inserted: confirm_link)<br/>- \"sales_lead_confirmed\" used to communicate a sales lead has been confirmed (variables to be inserted: customer)<br/>- \"password_recovery\" used to allow a new customer to reset a password (variables to be inserted: recovery_link and recovery_code)",
                "operationId": "getApiTemplate",
                "parameters": [
                    {
                        "default": 1,
                        "description": "page requested",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 1000 entries is the maximum allowed value",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "collectionFormat": "csv",
                        "default": [
                            "id"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "by default all the fields are returned but if a subset is required, list all the ones that should be included in the response",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "fields",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "templates list",
                        "schema": {
                            "items": {
                                "properties": {
                                    "created": {
                                        "type": "string"
                                    },
                                    "from_email": {
                                        "type": "string"
                                    },
                                    "id": {
                                        "type": "string"
                                    },
                                    "language": {
                                        "type": "string"
                                    },
                                    "name": {
                                        "type": "string"
                                    },
                                    "network_operator": {
                                        "type": "string"
                                    },
                                    "service_provider": {
                                        "type": "string"
                                    },
                                    "subject": {
                                        "type": "string"
                                    },
                                    "template": {
                                        "type": "string"
                                    },
                                    "template_number": {
                                        "type": "string"
                                    },
                                    "type": {
                                        "type": "string"
                                    },
                                    "updated": {
                                        "type": "string"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "404": {
                        "description": "no templates found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get templates",
                "tags": [
                    "api"
                ]
            },
            "post": {
                "description": "Create a new template.",
                "parameters": [
                    {
                        "description": "template to be added",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "from_email": {
                                    "type": "string"
                                },
                                "language": {
                                    "type": "string"
                                },
                                "name": {
                                    "type": "string"
                                },
                                "network_operator": {
                                    "type": "string"
                                },
                                "service_provider": {
                                    "type": "string"
                                },
                                "subject": {
                                    "type": "string"
                                },
                                "template": {
                                    "type": "string"
                                },
                                "type": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "language",
                                "template",
                                "type",
                                "name"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "201": {
                        "description": "template created"
                    },
                    "400": {
                        "description": "bad request or field values not valid"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Create a new template.",
                "tags": [
                    "api"
                ]
            },
            "put": {
                "description": "Update a template.",
                "parameters": [
                    {
                        "description": "update a template",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "from_email": {
                                    "type": "string"
                                },
                                "id": {
                                    "type": "string"
                                },
                                "language": {
                                    "type": "string"
                                },
                                "name": {
                                    "type": "string"
                                },
                                "network_operator": {
                                    "type": "string"
                                },
                                "service_provider": {
                                    "type": "string"
                                },
                                "subject": {
                                    "type": "string"
                                },
                                "template": {
                                    "type": "string"
                                },
                                "type": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "id"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "zone has been updated"
                    },
                    "400": {
                        "description": "bad request or field not valid"
                    },
                    "403": {
                        "description": "permission"
                    },
                    "404": {
                        "description": "template not found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Update a template.",
                "tags": [
                    "api"
                ]
            }
        },
        "/api/user": {
            "get": {
                "description": "Returns a list of users",
                "operationId": "getApiUser",
                "parameters": [
                    {
                        "default": 1,
                        "description": "page requested",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 1000 entries is the maximum allowed value",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "collectionFormat": "csv",
                        "default": [
                            "id"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "by default all the fields are returned but if a subset is required, list all the ones that should be included in the response",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "fields",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "customers list",
                        "schema": {
                            "items": {
                                "properties": {
                                    "created": {
                                        "type": "string"
                                    },
                                    "created_by": {
                                        "type": "string"
                                    },
                                    "email": {
                                        "type": "string"
                                    },
                                    "first_name": {
                                        "type": "string"
                                    },
                                    "id": {
                                        "type": "string"
                                    },
                                    "last_name": {
                                        "type": "string"
                                    },
                                    "network_operator": {
                                        "type": "string"
                                    },
                                    "notes": {
                                        "type": "string"
                                    },
                                    "password": {
                                        "type": "string"
                                    },
                                    "profile": {
                                        "type": "string"
                                    },
                                    "readonly": {
                                        "type": "string"
                                    },
                                    "role": {
                                        "type": "string"
                                    },
                                    "service_provider": {
                                        "type": "string"
                                    },
                                    "status": {
                                        "type": "string"
                                    },
                                    "updated": {
                                        "type": "string"
                                    },
                                    "updated_by": {
                                        "type": "string"
                                    },
                                    "username": {
                                        "type": "string"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "404": {
                        "description": "no customer records found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get a list of users",
                "tags": [
                    "api"
                ]
            },
            "post": {
                "description": "Add an user",
                "operationId": "postApiUser",
                "parameters": [
                    {
                        "description": "user to be added",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "email": {
                                    "type": "string"
                                },
                                "first_name": {
                                    "type": "string"
                                },
                                "last_name": {
                                    "type": "string"
                                },
                                "network_operator": {
                                    "type": "string"
                                },
                                "password": {
                                    "type": "string"
                                },
                                "readonly": {
                                    "type": "string"
                                },
                                "role": {
                                    "type": "string"
                                },
                                "service_provider": {
                                    "type": "string"
                                },
                                "username": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "username",
                                "first_name",
                                "last_name",
                                "email",
                                "role",
                                "password"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "201": {
                        "description": "user succesfully added"
                    },
                    "406": {
                        "description": "error from the backend server"
                    },
                    "409": {
                        "description": "user can not be added some parameters are missed or wrong"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Add an user",
                "tags": [
                    "api"
                ]
            },
            "put": {
                "description": "Update an user",
                "operationId": "putApiUser",
                "parameters": [
                    {
                        "description": "user to be updated",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "email": {
                                    "type": "string"
                                },
                                "first_name": {
                                    "type": "string"
                                },
                                "id": {
                                    "type": "string"
                                },
                                "last_name": {
                                    "type": "string"
                                },
                                "network_operator": {
                                    "type": "string"
                                },
                                "password": {
                                    "type": "string"
                                },
                                "readonly": {
                                    "type": "string"
                                },
                                "role": {
                                    "type": "string"
                                },
                                "service_provider": {
                                    "type": "string"
                                },
                                "status": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "id"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "user succesfully updated"
                    },
                    "401": {
                        "description": "user not found"
                    },
                    "406": {
                        "description": "error from the backend server"
                    },
                    "409": {
                        "description": "user can not be updated because some parameters are missed or wrong"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Update an user",
                "tags": [
                    "api"
                ]
            }
        },
        "/api/user/password": {
            "get": {
                "description": "Password recovery and change without login. Only works for customer users.<br/>The recovery works with an initial get of username or email which triggers<br/>the sending of an email with a recovery code. With the recovery code password<br/>can be changed with a put.",
                "operationId": "getApiUserPassword",
                "parameters": [
                    {
                        "description": "user username or email",
                        "in": "query",
                        "name": "username_or_email",
                        "type": "string"
                    },
                    {
                        "description": "portal url that will be used in the email sent",
                        "in": "query",
                        "name": "url",
                        "type": "string"
                    },
                    {
                        "description": "specify if the passed username is a user or a customer (default)",
                        "in": "query",
                        "name": "usertype",
                        "type": "string"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "email sent"
                    },
                    "404": {
                        "description": "no user found"
                    }
                },
                "summary": "Send password recovery code",
                "tags": [
                    "api"
                ]
            },
            "put": {
                "description": "Set password using recovery code.",
                "operationId": "putApiUserPassword",
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "password": {
                                    "type": "string"
                                },
                                "recovery_code": {
                                    "type": "string"
                                },
                                "usertype": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "recovery_code",
                                "password",
                                "usertype"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "password has been changed"
                    },
                    "404": {
                        "description": "no user found"
                    }
                },
                "summary": "Set password",
                "tags": [
                    "api"
                ]
            }
        },
        "/api/user/settings": {
            "delete": {
                "description": "Delete the user settings record. Username and settings id must be provided.",
                "parameters": [
                    {
                        "description": "deleted user settings record",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "created": {
                                    "type": "string"
                                },
                                "id": {
                                    "type": "string"
                                },
                                "name": {
                                    "type": "string"
                                },
                                "settings": {
                                    "type": "string"
                                },
                                "updated": {
                                    "type": "string"
                                },
                                "user": {
                                    "type": "string"
                                },
                                "username": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "username",
                                "updated",
                                "name",
                                "created",
                                "settings",
                                "user",
                                "id"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "user settings record has been deleted"
                    },
                    "400": {
                        "description": "the id supplier is not a valid GUID"
                    },
                    "404": {
                        "description": "user settings record was not found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Delete a user settings record",
                "tags": [
                    "api"
                ]
            },
            "get": {
                "description": "Returns a list of user settings available for the user.",
                "operationId": "getUserSettings",
                "parameters": [
                    {
                        "default": 1,
                        "description": "page requested",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 1000 entries is the maximum allowed value",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "collectionFormat": "csv",
                        "default": [
                            "id"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "by default all the fields are returned but if a subset is required, list all the ones that should be included in the response",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "fields",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "settings record list for the user",
                        "schema": {
                            "items": {
                                "properties": {
                                    "created": {
                                        "type": "string"
                                    },
                                    "id": {
                                        "type": "string"
                                    },
                                    "name": {
                                        "type": "string"
                                    },
                                    "settings": {
                                        "type": "string"
                                    },
                                    "updated": {
                                        "type": "string"
                                    },
                                    "user": {
                                        "type": "string"
                                    },
                                    "username": {
                                        "type": "string"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "404": {
                        "description": "no settings records found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get user settings",
                "tags": [
                    "api"
                ]
            },
            "post": {
                "description": "Create a new user settings record. Username, settings name and settings must be provided.",
                "operationId": "postUserSettings",
                "parameters": [
                    {
                        "description": "user settings record to be added",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "name": {
                                    "type": "string"
                                },
                                "settings": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "name",
                                "settings"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "201": {
                        "description": "created settings"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Create a new user settings record",
                "tags": [
                    "api"
                ]
            },
            "put": {
                "description": "Update a user settings record. Username, settings name and settings must be provided.",
                "operationId": "putUserSettings",
                "parameters": [
                    {
                        "description": "updated user settings record",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "name": {
                                    "type": "string"
                                },
                                "settings": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "name",
                                "settings"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "user settings record has been updated"
                    },
                    "400": {
                        "description": "the id supplier is not a valid GUID"
                    },
                    "404": {
                        "description": "user settings record was not found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Update a user settings record",
                "tags": [
                    "api"
                ]
            }
        },
        "/bundle": {
            "delete": {
                "description": "Delete a Service Bundle",
                "operationId": "deleteBundle",
                "parameters": [
                    {
                        "description": "Delete a Service Bundle",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "id": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "id"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Service Bundle has been deleted"
                    },
                    "400": {
                        "description": "Generic error"
                    },
                    "403": {
                        "description": "Permission issue"
                    },
                    "404": {
                        "description": "Service Bundle not found"
                    },
                    "406": {
                        "description": "Error"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Delete a Service Bundle",
                "tags": [
                    "service"
                ]
            },
            "get": {
                "description": "Returns a list of Service Bundles",
                "operationId": "getBundle",
                "parameters": [
                    {
                        "default": 1,
                        "description": "page requested",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 1000 entries is the maximum allowed value",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "collectionFormat": "csv",
                        "default": [
                            "id"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "by default all the fields are returned but if a subset is required, list all the ones that should be included in the response",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "fields",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Bundle list",
                        "schema": {
                            "items": {
                                "properties": {
                                    "bundle_number": {
                                        "type": "string"
                                    },
                                    "created": {
                                        "type": "string"
                                    },
                                    "customer_type": {
                                        "type": "string"
                                    },
                                    "description": {
                                        "type": "string"
                                    },
                                    "id": {
                                        "type": "string"
                                    },
                                    "name": {
                                        "type": "string"
                                    },
                                    "network_operator": {
                                        "type": "string"
                                    },
                                    "services": {
                                        "type": "string"
                                    },
                                    "updated": {
                                        "type": "string"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "403": {
                        "description": "not authorized to access"
                    },
                    "404": {
                        "description": "no Bundle records found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get a list of Service Bundles",
                "tags": [
                    "service"
                ]
            },
            "post": {
                "description": "Create a Bundle",
                "operationId": "postBundle",
                "parameters": [
                    {
                        "description": "Create a Service Bundle",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "customer_type": {
                                    "type": "string"
                                },
                                "description": {
                                    "type": "string"
                                },
                                "name": {
                                    "type": "string"
                                },
                                "network_operator": {
                                    "type": "string"
                                },
                                "services": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "network_operator",
                                "services",
                                "name"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "201": {
                        "description": "Bundle has been added"
                    },
                    "406": {
                        "description": "Error from backend server"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Create a Bundle",
                "tags": [
                    "service"
                ]
            },
            "put": {
                "description": "Edit a Service Bundle",
                "operationId": "putBundle",
                "parameters": [
                    {
                        "description": "Update a Service Bundle",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "customer_type": {
                                    "type": "string"
                                },
                                "description": {
                                    "type": "string"
                                },
                                "id": {
                                    "type": "string"
                                },
                                "name": {
                                    "type": "string"
                                },
                                "network_operator": {
                                    "type": "string"
                                },
                                "services": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "id"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Service Bundle has been updated"
                    },
                    "400": {
                        "description": "Generic Error"
                    },
                    "404": {
                        "description": "Service Bundle was not found"
                    },
                    "406": {
                        "description": "Error from backend server"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Edit a Service Bundle",
                "tags": [
                    "service"
                ]
            }
        },
        "/bundle/view": {
            "get": {
                "description": "Returns a view of Service Bundles",
                "operationId": "getBundleView",
                "parameters": [
                    {
                        "description": "bundle id or bundle_number",
                        "in": "query",
                        "name": "bundle",
                        "type": "string"
                    },
                    {
                        "description": "object id where the bundle is applied",
                        "in": "query",
                        "name": "object",
                        "type": "string"
                    },
                    {
                        "description": "object_group where the bundle is applied",
                        "in": "query",
                        "name": "object_group",
                        "type": "string"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Bundle list",
                        "schema": {
                            "properties": {
                                "data": {
                                    "properties": {
                                        "bundle_number": {
                                            "type": "string"
                                        },
                                        "customer_type": {
                                            "type": "string"
                                        },
                                        "description": {
                                            "type": "string"
                                        },
                                        "id": {
                                            "type": "string"
                                        },
                                        "name": {
                                            "type": "string"
                                        },
                                        "network_operator": {
                                            "type": "string"
                                        },
                                        "services": {
                                            "type": "string"
                                        },
                                        "survey_result": {
                                            "type": "string"
                                        }
                                    },
                                    "type": "object"
                                },
                                "message": {
                                    "type": "string"
                                }
                            },
                            "type": "object"
                        }
                    },
                    "403": {
                        "description": "not authorized to access"
                    },
                    "404": {
                        "description": "no Bundle records found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get a view of Service Bundles",
                "tags": [
                    "service"
                ]
            }
        },
        "/customer": {
            "delete": {
                "description": "Delete a Customer",
                "operationId": "deleteCustomer",
                "parameters": [
                    {
                        "description": "Delete a Customer",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "id": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "id"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Customer has been deleted"
                    },
                    "404": {
                        "$ref": "#/responses/404NotFound"
                    },
                    "406": {
                        "$ref": "#/responses/406NotAcceptable"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Delete a Customer",
                "tags": [
                    "customer"
                ]
            },
            "get": {
                "description": "Returns a list of customers<br/><br/>Note: A VxAPI setting can enable a limitatio for Service Providers: they can query only a single customer providing its email",
                "operationId": "getCustomer",
                "parameters": [
                    {
                        "default": 1,
                        "description": "page requested",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 1000 entries is the maximum allowed value",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "collectionFormat": "csv",
                        "default": [
                            "id"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "by default all the fields are returned but if a subset is required, list all the ones that should be included in the response",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "fields",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "customers list",
                        "schema": {
                            "properties": {
                                "data": {
                                    "items": {
                                        "$ref": "#/definitions/Customer"
                                    },
                                    "type": "array"
                                }
                            },
                            "type": "object"
                        }
                    },
                    "404": {
                        "$ref": "#/responses/404NotFound"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get a list of customers",
                "tags": [
                    "customer"
                ]
            },
            "post": {
                "description": "Add a new customer",
                "operationId": "postCustomer",
                "parameters": [
                    {
                        "description": "customer to be added",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "b_address": {
                                    "type": "string"
                                },
                                "b_city": {
                                    "type": "string"
                                },
                                "b_full_name": {
                                    "type": "string"
                                },
                                "b_postal_code": {
                                    "type": "string"
                                },
                                "c_o": {
                                    "type": "string"
                                },
                                "city": {
                                    "type": "string"
                                },
                                "company_name": {
                                    "type": "string"
                                },
                                "country": {
                                    "type": "string"
                                },
                                "country_code": {
                                    "type": "string"
                                },
                                "customer_type": {
                                    "type": "string"
                                },
                                "email": {
                                    "type": "string"
                                },
                                "first_name": {
                                    "type": "string"
                                },
                                "language": {
                                    "type": "string"
                                },
                                "last_name": {
                                    "type": "string"
                                },
                                "mobile_number": {
                                    "type": "string"
                                },
                                "password": {
                                    "type": "string"
                                },
                                "phone_number": {
                                    "type": "string"
                                },
                                "postal_code": {
                                    "type": "string"
                                },
                                "province": {
                                    "type": "string"
                                },
                                "reference": {
                                    "type": "string"
                                },
                                "ssn": {
                                    "type": "string"
                                },
                                "street_address": {
                                    "type": "string"
                                },
                                "username": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "last_name",
                                "postal_code",
                                "city",
                                "first_name",
                                "province",
                                "phone_number",
                                "mobile_number",
                                "password",
                                "language",
                                "email",
                                "customer_type",
                                "street_address"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "201": {
                        "description": "Customer has been added",
                        "schema": {
                            "properties": {
                                "data": {
                                    "$ref": "#/definitions/Customer"
                                },
                                "message": {
                                    "type": "string"
                                }
                            },
                            "type": "object"
                        }
                    },
                    "406": {
                        "$ref": "#/responses/406NotAcceptable"
                    },
                    "400": {
                        "$ref": "#/responses/400BadRequest"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Add a new customer",
                "tags": [
                    "customer"
                ]
            },
            "put": {
                "description": "Update the customer with a specific id, if exists",
                "operationId": "putCustomer",
                "parameters": [
                    {
                        "description": "updated customer",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "b_address": {
                                    "type": "string"
                                },
                                "b_city": {
                                    "type": "string"
                                },
                                "b_full_name": {
                                    "type": "string"
                                },
                                "b_postal_code": {
                                    "type": "string"
                                },
                                "c_o": {
                                    "type": "string"
                                },
                                "city": {
                                    "type": "string"
                                },
                                "company_name": {
                                    "type": "string"
                                },
                                "country": {
                                    "type": "string"
                                },
                                "country_code": {
                                    "type": "string"
                                },
                                "customer_type": {
                                    "type": "string"
                                },
                                "email": {
                                    "type": "string"
                                },
                                "first_name": {
                                    "type": "string"
                                },
                                "id": {
                                    "type": "string"
                                },
                                "language": {
                                    "type": "string"
                                },
                                "last_name": {
                                    "type": "string"
                                },
                                "mobile_number": {
                                    "type": "string"
                                },
                                "password": {
                                    "type": "string"
                                },
                                "phone_number": {
                                    "type": "string"
                                },
                                "postal_code": {
                                    "type": "string"
                                },
                                "province": {
                                    "type": "string"
                                },
                                "reference": {
                                    "type": "string"
                                },
                                "ssn": {
                                    "type": "string"
                                },
                                "street_address": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "id"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "customer has been updated",
                        "schema": {
                            "properties": {
                                "data": {
                                    "$ref": "#/definitions/Customer"
                                },
                                "message": {
                                    "type": "string"
                                }
                            },
                            "type": "object"
                        }
                    },
                    "400": {
                        "$ref": "#/responses/400BadRequest"
                    },
                    "404": {
                        "$ref": "#/responses/404NotFound"
                    },
                    "406": {
                        "$ref": "#/responses/406NotAcceptable"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Update a customer",
                "tags": [
                    "customer"
                ]
            }
        },
        "/customer/password": {
            "get": {
                "description": "Password recovery and change without login for customer users.<br/>The recovery works with an initial get of username or email which triggers<br/>the sending of an email with a recovery code. With the recovery code password<br/>can be changed with a put.",
                "operationId": "getCustomerPassword",
                "parameters": [
                    {
                        "description": "user username or email",
                        "in": "query",
                        "name": "username_or_email",
                        "type": "string"
                    },
                    {
                        "description": "portal url that will be used in the email sent",
                        "in": "query",
                        "name": "url",
                        "type": "string"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Email sent"
                    },
                    "404": {
                        "$ref": "#/responses/404NotFound"
                    },
                    "406": {
                        "$ref": "#/responses/406NotAcceptable"
                    }
                },
                "summary": "Send password recovery code",
                "tags": [
                    "customer"
                ]
            },
            "put": {
                "description": "Set password using recovery code.",
                "operationId": "putCustomerPassword",
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "password": {
                                    "type": "string"
                                },
                                "recovery_code": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "recovery_code",
                                "password"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Password has been changed"
                    },
                    "404": {
                        "$ref": "#/responses/404NotFound"
                    }
                },
                "summary": "Set password",
                "tags": [
                    "api"
                ]
            }
        },
        "/customer_objects": {
            "get": {
                "description": "List of all object associted (now or in the past) to the provided customer",
                "operationId": "getCustomerObjects",
                "parameters": [
                    {
                        "description": "limit the scope only to the statistics that belong to the id of the provided network_operator",
                        "in": "query",
                        "name": "network_operator",
                        "type": "string"
                    },
                    {
                        "description": "identify the customer.",
                        "in": "query",
                        "name": "customer_id",
                        "type": "string"
                    },
                    {
                        "description": "identify the customer.",
                        "in": "query",
                        "name": "customer_number",
                        "type": "string"
                    },
                    {
                        "default": 1,
                        "description": "requested page",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 0 to disable the limit and gives back all the entries",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "default": [
                            "created"
                        ],
                        "description": "fields we want items to be order by ; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Objects associated to the customer",
                        "schema": {
                            "properties": {
                                "data": {
                                    "$ref": "#/definitions/Object"
                                },
                                "message": {
                                    "type": "string"
                                }
                            },
                            "type": "object"
                        }
                    },
                    "400": {
                        "$ref": "#/responses/400BadRequest"
                    },
                    "404": {
                        "$ref": "#/responses/404NotFound"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Objects related to the provided customer",
                "tags": [
                    "customer"
                ]
            }
        },
        "/file": {
            "delete": {
                "description": "Delete a File",
                "parameters": [
                    {
                        "description": "deleted a file",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "id": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "id"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "File has been deleted"
                    },
                    "403": {
                        "description": "Permission issue"
                    },
                    "404": {
                        "description": "File not found"
                    },
                    "406": {
                        "description": "Backend error"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Delete a File",
                "tags": [
                    "file"
                ]
            },
            "get": {
                "description": "Returns a list of files and their contents in base64 or binary format",
                "parameters": [
                    {
                        "default": 1,
                        "description": "page requested",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 1000 entries is the maximum allowed value",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "collectionFormat": "csv",
                        "default": [
                            "id"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "by default all the fields are returned but if a subset is required, list all the ones that should be included in the response",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "fields",
                        "type": "array"
                    },
                    {
                        "description": "the format of the file; available format are json, image or file; for the last two only one file need to be selected with proper query (default json)",
                        "in": "query",
                        "name": "format",
                        "type": "string"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "file list list",
                        "schema": {
                            "items": {
                                "properties": {
                                    "content_type": {
                                        "type": "string"
                                    },
                                    "created": {
                                        "type": "string"
                                    },
                                    "data": {
                                        "type": "string"
                                    },
                                    "file_type": {
                                        "type": "string"
                                    },
                                    "filename": {
                                        "type": "string"
                                    },
                                    "id": {
                                        "type": "string"
                                    },
                                    "name": {
                                        "type": "string"
                                    },
                                    "service_provider": {
                                        "type": "string"
                                    },
                                    "updated": {
                                        "type": "string"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "404": {
                        "description": "no service provider records found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get a list of file",
                "tags": [
                    "file"
                ]
            },
            "post": {
                "description": "Upload a file",
                "parameters": [
                    {
                        "description": "Upload a file",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "content_type": {
                                    "type": "string"
                                },
                                "data": {
                                    "type": "string"
                                },
                                "file_type": {
                                    "type": "string"
                                },
                                "filename": {
                                    "type": "string"
                                },
                                "name": {
                                    "type": "string"
                                },
                                "service_provider": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "name",
                                "file_type",
                                "filename",
                                "content_type",
                                "service_provider",
                                "data"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "201": {
                        "description": "file has been created"
                    },
                    "400": {
                        "description": "bad formatting"
                    },
                    "402": {
                        "description": "file too big"
                    },
                    "405": {
                        "description": "base64 encoded string is not valid"
                    },
                    "406": {
                        "description": "error from backend server"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Upload a file",
                "tags": [
                    "file"
                ]
            },
            "put": {
                "description": "Update a file",
                "parameters": [
                    {
                        "description": "Update a file",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "content_type": {
                                    "type": "string"
                                },
                                "data": {
                                    "type": "string"
                                },
                                "file_type": {
                                    "type": "string"
                                },
                                "filename": {
                                    "type": "string"
                                },
                                "id": {
                                    "type": "string"
                                },
                                "name": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "id"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "file has been updated"
                    },
                    "400": {
                        "description": "bad formatting"
                    },
                    "402": {
                        "description": "file too big"
                    },
                    "405": {
                        "description": "base64 encoded string is not valid"
                    },
                    "406": {
                        "description": "error from backend server"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Update a file",
                "tags": [
                    "file"
                ]
            }
        },
        "/inventory/sdd": {
            "get": {
                "description": "Returns a list of switch from the Inventory.",
                "parameters": [
                    {
                        "default": 1,
                        "description": "page requested",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 1000 entries is the maximum allowed value",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "collectionFormat": "csv",
                        "default": [
                            "id"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "by default all the fields are returned but if a subset is required, list all the ones that should be included in the response",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "fields",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "inventory switches record list",
                        "schema": {
                            "items": {
                                "properties": {
                                    "created": {
                                        "type": "string"
                                    },
                                    "device_model": {
                                        "type": "string"
                                    },
                                    "id": {
                                        "type": "string"
                                    },
                                    "inventory_status": {
                                        "type": "string"
                                    },
                                    "ip_address": {
                                        "type": "string"
                                    },
                                    "last_seen": {
                                        "type": "string"
                                    },
                                    "lifecycle_status": {
                                        "type": "string"
                                    },
                                    "mac": {
                                        "type": "string"
                                    },
                                    "object": {
                                        "type": "string"
                                    },
                                    "object_group": {
                                        "type": "string"
                                    },
                                    "object_name": {
                                        "type": "string"
                                    },
                                    "updated": {
                                        "type": "string"
                                    },
                                    "version": {
                                        "type": "string"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "404": {
                        "description": "no switch found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get inventory SDD items",
                "tags": [
                    "inventory"
                ]
            }
        },
        "/inventory/switch": {
            "get": {
                "description": "Returns a list of switch from the Inventory.",
                "parameters": [
                    {
                        "default": 1,
                        "description": "page requested",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 1000 entries is the maximum allowed value",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "collectionFormat": "csv",
                        "default": [
                            "id"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "by default all the fields are returned but if a subset is required, list all the ones that should be included in the response",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "fields",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "inventory switches record list",
                        "schema": {
                            "items": {
                                "properties": {
                                    "created": {
                                        "type": "string"
                                    },
                                    "device_model": {
                                        "type": "string"
                                    },
                                    "id": {
                                        "type": "string"
                                    },
                                    "inventory_status": {
                                        "type": "string"
                                    },
                                    "ip_address": {
                                        "type": "string"
                                    },
                                    "last_seen": {
                                        "type": "string"
                                    },
                                    "lifecycle_status": {
                                        "type": "string"
                                    },
                                    "mac": {
                                        "type": "string"
                                    },
                                    "network": {
                                        "type": "string"
                                    },
                                    "site": {
                                        "type": "string"
                                    },
                                    "stack_role": {
                                        "type": "string"
                                    },
                                    "switch": {
                                        "type": "string"
                                    },
                                    "switch_driver": {
                                        "type": "string"
                                    },
                                    "switch_model": {
                                        "type": "string"
                                    },
                                    "switch_name": {
                                        "type": "string"
                                    },
                                    "switch_type": {
                                        "type": "string"
                                    },
                                    "updated": {
                                        "type": "string"
                                    },
                                    "version": {
                                        "type": "string"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "404": {
                        "description": "no switch found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get inventory Switch items",
                "tags": [
                    "inventory"
                ]
            }
        },
        "/invoice": {
            "get": {
                "description": "Returns a invoice summary",
                "operationId": "getInvoice",
                "parameters": [
                    {
                        "description": "month (1 .. 12)",
                        "in": "query",
                        "name": "month",
                        "type": "string"
                    },
                    {
                        "description": "year (>= 2014)",
                        "in": "query",
                        "name": "year",
                        "type": "string"
                    },
                    {
                        "description": "network_operator id (optional)",
                        "in": "query",
                        "name": "network_operator",
                        "type": "string"
                    },
                    {
                        "description": "object group id (optional)",
                        "in": "query",
                        "name": "object_group",
                        "type": "string"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "invoice items list"
                    },
                    "404": {
                        "description": "no invoice found"
                    },
                    "406": {
                        "description": "incorrect or missing parameters"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Report invoice summary",
                "tags": [
                    "invoice"
                ]
            }
        },
        "/invoice_items": {
            "get": {
                "description": "Returns a list of invoice items",
                "operationId": "getInvoiceItems",
                "parameters": [
                    {
                        "default": 1,
                        "description": "page requested",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 1000 entries is the maximum allowed value",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "collectionFormat": "csv",
                        "default": [
                            "id"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "by default all the fields are returned but if a subset is required, list all the ones that should be included in the response",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "fields",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "invoice items list",
                        "schema": {
                            "items": {
                                "properties": {
                                    "city": {
                                        "type": "string"
                                    },
                                    "created": {
                                        "type": "string"
                                    },
                                    "customer": {
                                        "type": "string"
                                    },
                                    "customer_number": {
                                        "type": "string"
                                    },
                                    "fee": {
                                        "type": "string"
                                    },
                                    "fee_type": {
                                        "type": "string"
                                    },
                                    "fee_type_name": {
                                        "type": "string"
                                    },
                                    "first_name": {
                                        "type": "string"
                                    },
                                    "from_date": {
                                        "type": "string"
                                    },
                                    "id": {
                                        "type": "string"
                                    },
                                    "item_type": {
                                        "type": "string"
                                    },
                                    "last_name": {
                                        "type": "string"
                                    },
                                    "month": {
                                        "type": "string"
                                    },
                                    "network_operator": {
                                        "type": "string"
                                    },
                                    "network_operator_name": {
                                        "type": "string"
                                    },
                                    "note": {
                                        "type": "string"
                                    },
                                    "object": {
                                        "type": "string"
                                    },
                                    "object_city": {
                                        "type": "string"
                                    },
                                    "object_group": {
                                        "type": "string"
                                    },
                                    "object_group_name": {
                                        "type": "string"
                                    },
                                    "object_number": {
                                        "type": "string"
                                    },
                                    "object_postal_code": {
                                        "type": "string"
                                    },
                                    "object_province": {
                                        "type": "string"
                                    },
                                    "object_street": {
                                        "type": "string"
                                    },
                                    "object_street_number": {
                                        "type": "string"
                                    },
                                    "order_id": {
                                        "type": "string"
                                    },
                                    "order_number": {
                                        "type": "string"
                                    },
                                    "postal_code": {
                                        "type": "string"
                                    },
                                    "province": {
                                        "type": "string"
                                    },
                                    "quantity": {
                                        "type": "string"
                                    },
                                    "service": {
                                        "type": "string"
                                    },
                                    "service_name": {
                                        "type": "string"
                                    },
                                    "service_provider": {
                                        "type": "string"
                                    },
                                    "service_provider_name": {
                                        "type": "string"
                                    },
                                    "service_type": {
                                        "type": "string"
                                    },
                                    "service_type_name": {
                                        "type": "string"
                                    },
                                    "street_address": {
                                        "type": "string"
                                    },
                                    "to_date": {
                                        "type": "string"
                                    },
                                    "total_cost": {
                                        "type": "string"
                                    },
                                    "updated": {
                                        "type": "string"
                                    },
                                    "year": {
                                        "type": "string"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "404": {
                        "description": "no invoice items found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get a list of items of a invoice",
                "tags": [
                    "invoice"
                ]
            }
        },
        "/ip_address": {
            "delete": {
                "description": "Delete a IP Address from the database. Static Ip Address will be deleted also on the Provisioning System",
                "parameters": [
                    {
                        "description": "deleted IP Address",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "id": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "id"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "IP Address has been deleted"
                    },
                    "403": {
                        "description": "permission issue"
                    },
                    "404": {
                        "description": "IP Address not found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Delete a IP Address",
                "tags": [
                    "network"
                ]
            },
            "get": {
                "description": "Returns a list of IP Addresss.",
                "operationId": "getIpAddress",
                "parameters": [
                    {
                        "default": 1,
                        "description": "page requested",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 1000 entries is the maximum allowed value",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "collectionFormat": "csv",
                        "default": [
                            "id"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "by default all the fields are returned but if a subset is required, list all the ones that should be included in the response",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "fields",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "IP Address list",
                        "schema": {
                            "items": {
                                "properties": {
                                    "id": {
                                        "type": "string"
                                    },
                                    "ip_address": {
                                        "type": "string"
                                    },
                                    "ip_subnet": {
                                        "type": "string"
                                    },
                                    "lease": {
                                        "type": "string"
                                    },
                                    "mac": {
                                        "type": "string"
                                    },
                                    "network_operator": {
                                        "type": "string"
                                    },
                                    "object": {
                                        "type": "string"
                                    },
                                    "object_group": {
                                        "type": "string"
                                    },
                                    "object_number": {
                                        "type": "string"
                                    },
                                    "service_provider": {
                                        "type": "string"
                                    },
                                    "updated": {
                                        "type": "string"
                                    },
                                    "vlan": {
                                        "type": "string"
                                    },
                                    "vlan_id": {
                                        "type": "string"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "403": {
                        "description": "not authorized to access"
                    },
                    "404": {
                        "description": "no IP Address found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get IP Address",
                "tags": [
                    "network"
                ]
            },
            "post": {
                "description": "Add a new IP Address in the database. Only static IP request are sent to the Provisioning System.",
                "operationId": "postIpAddress",
                "parameters": [
                    {
                        "description": "IP Address to be added",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "ip_address": {
                                    "type": "string"
                                },
                                "ip_subnet": {
                                    "type": "string"
                                },
                                "lease": {
                                    "type": "string"
                                },
                                "mac": {
                                    "type": "string"
                                },
                                "object": {
                                    "type": "string"
                                },
                                "object_number": {
                                    "type": "string"
                                },
                                "vlan": {
                                    "type": "string"
                                },
                                "vlan_id": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "mac",
                                "lease"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "201": {
                        "description": "IP Address created"
                    },
                    "400": {
                        "description": "bad request or field values not valid"
                    },
                    "404": {
                        "description": "one or more of the provided field does not exists"
                    },
                    "406": {
                        "description": "backend error"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Add a new IP Address.",
                "tags": [
                    "network"
                ]
            },
            "put": {
                "description": "Update a IP Address in the database. No action on the Provisioning System are executed",
                "operationId": "putIpAddress",
                "parameters": [
                    {
                        "description": "IP Address to be updated",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "ip_address": {
                                    "type": "string"
                                },
                                "ip_subnet": {
                                    "type": "string"
                                },
                                "lease": {
                                    "type": "string"
                                },
                                "mac": {
                                    "type": "string"
                                },
                                "object": {
                                    "type": "string"
                                },
                                "object_number": {
                                    "type": "string"
                                },
                                "vlan": {
                                    "type": "string"
                                },
                                "vlan_id": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "mac",
                                "lease"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "IP Address updated"
                    },
                    "400": {
                        "description": "bad request or field values not valid"
                    },
                    "404": {
                        "description": "one or more of the provided field does not exists"
                    },
                    "406": {
                        "description": "backend error"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Update a IP Address.",
                "tags": [
                    "network"
                ]
            }
        },
        "/ip_subnet": {
            "delete": {
                "description": "Delete a IP Subnet",
                "operationId": "deleteIpSubnet",
                "parameters": [
                    {
                        "description": "deleted IP Subnet",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "id": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "id"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "IP Subnet has been deleted"
                    },
                    "403": {
                        "description": "permission issue"
                    },
                    "404": {
                        "description": "IP Subnet not found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Delete a IP Subnet",
                "tags": [
                    "network"
                ]
            },
            "get": {
                "description": "Returns a list of IP Subnets.",
                "operationId": "getIpSubnet",
                "parameters": [
                    {
                        "default": 1,
                        "description": "page requested",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 1000 entries is the maximum allowed value",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "collectionFormat": "csv",
                        "default": [
                            "id"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "by default all the fields are returned but if a subset is required, list all the ones that should be included in the response",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "fields",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "IP Subnets list",
                        "schema": {
                            "items": {
                                "properties": {
                                    "active_ips": {
                                        "type": "string"
                                    },
                                    "created": {
                                        "type": "string"
                                    },
                                    "dns1": {
                                        "type": "string"
                                    },
                                    "dns2": {
                                        "type": "string"
                                    },
                                    "domain": {
                                        "type": "string"
                                    },
                                    "gateway": {
                                        "type": "string"
                                    },
                                    "id": {
                                        "type": "string"
                                    },
                                    "name": {
                                        "type": "string"
                                    },
                                    "netmask": {
                                        "type": "string"
                                    },
                                    "network": {
                                        "type": "string"
                                    },
                                    "number_ips": {
                                        "type": "string"
                                    },
                                    "reclaim": {
                                        "type": "string"
                                    },
                                    "service_provider": {
                                        "type": "string"
                                    },
                                    "status": {
                                        "type": "string"
                                    },
                                    "type": {
                                        "type": "string"
                                    },
                                    "updated": {
                                        "type": "string"
                                    },
                                    "used_ips": {
                                        "type": "string"
                                    },
                                    "vlan": {
                                        "type": "string"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "403": {
                        "description": "not authorized to access"
                    },
                    "404": {
                        "description": "no IP Subnets found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get a list of IP Subnets",
                "tags": [
                    "network"
                ]
            },
            "post": {
                "description": "Create a new IP Subnet.",
                "operationId": "postIpSubnet",
                "parameters": [
                    {
                        "description": "IP Subnet to be added",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "dns1": {
                                    "type": "string"
                                },
                                "dns2": {
                                    "type": "string"
                                },
                                "domain": {
                                    "type": "string"
                                },
                                "gateway": {
                                    "type": "string"
                                },
                                "name": {
                                    "type": "string"
                                },
                                "network": {
                                    "type": "string"
                                },
                                "reclaim": {
                                    "type": "string"
                                },
                                "vlan": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "network",
                                "name",
                                "vlan",
                                "gateway"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "201": {
                        "description": "IP Subnet created"
                    },
                    "400": {
                        "description": "bad request or field values not valid"
                    },
                    "404": {
                        "description": "one or more of the provided field does not exists"
                    },
                    "406": {
                        "description": "backend error"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Create a new IP Subnet.",
                "tags": [
                    "network"
                ]
            },
            "put": {
                "description": "Update a IP Subnet.",
                "operationId": "putIpSubnet",
                "parameters": [
                    {
                        "description": "IP Subnet fields that must be updated",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "dns1": {
                                    "type": "string"
                                },
                                "dns2": {
                                    "type": "string"
                                },
                                "id": {
                                    "type": "string"
                                },
                                "reclaim": {
                                    "type": "string"
                                },
                                "status": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "id"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "IP Subnet updated"
                    },
                    "400": {
                        "description": "bad request or field values not valid"
                    },
                    "404": {
                        "description": "one or more of the provided field does not exists"
                    },
                    "406": {
                        "description": "backend error"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Update a IP Subnet.",
                "tags": [
                    "network"
                ]
            }
        },
        "/network": {
            "get": {
                "description": "Returns a list of network",
                "parameters": [
                    {
                        "default": 1,
                        "description": "page requested",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 1000 entries is the maximum allowed value",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "collectionFormat": "csv",
                        "default": [
                            "id"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "by default all the fields are returned but if a subset is required, list all the ones that should be included in the response",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "fields",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "network operator list",
                        "schema": {
                            "items": {
                                "properties": {
                                    "created": {
                                        "type": "string"
                                    },
                                    "id": {
                                        "type": "string"
                                    },
                                    "name": {
                                        "type": "string"
                                    },
                                    "network_operator": {
                                        "type": "string"
                                    },
                                    "number": {
                                        "type": "string"
                                    },
                                    "switch": {
                                        "type": "string"
                                    },
                                    "updated": {
                                        "type": "string"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "403": {
                        "description": "not authorized to access"
                    },
                    "404": {
                        "description": "no network operators records found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get a list of network",
                "tags": [
                    "network"
                ]
            }
        },
        "/network/interface": {
            "get": {
                "description": "",
                "operationId": "getNetworkInterface",
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "the list of network interfaces"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get the list of network interfaces",
                "tags": [
                    "network"
                ]
            }
        },
        "/network/node": {
            "get": {
                "description": "",
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "the list network nodes"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get the list of network nodes",
                "tags": [
                    "network"
                ]
            }
        },
        "/network/vlan": {
            "delete": {
                "description": "Delete a Vlan",
                "parameters": [
                    {
                        "description": "Delete a Vlan",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "id": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "id"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Vlan has been deleted"
                    },
                    "403": {
                        "description": "Permission issue"
                    },
                    "404": {
                        "description": "Vlan not found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Delete a Vlan",
                "tags": [
                    "network"
                ]
            },
            "get": {
                "description": "Returns a list of network vlan",
                "parameters": [
                    {
                        "default": 1,
                        "description": "page requested",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 1000 entries is the maximum allowed value",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "collectionFormat": "csv",
                        "default": [
                            "id"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "by default all the fields are returned but if a subset is required, list all the ones that should be included in the response",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "fields",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "network operator list",
                        "schema": {
                            "items": {
                                "properties": {
                                    "id": {
                                        "type": "string"
                                    },
                                    "service_provider": {
                                        "type": "string"
                                    },
                                    "type": {
                                        "type": "string"
                                    },
                                    "vlan_id": {
                                        "type": "string"
                                    },
                                    "vlan_type": {
                                        "type": "string"
                                    },
                                    "vlan_type_name": {
                                        "type": "string"
                                    },
                                    "vlan_type_type": {
                                        "type": "string"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "403": {
                        "description": "not authorized to access"
                    },
                    "404": {
                        "description": "no network operators records found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get a list of network vlan",
                "tags": [
                    "network"
                ]
            },
            "post": {
                "description": "Create a Vlan",
                "parameters": [
                    {
                        "description": "Create a Vlan",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "type": {
                                    "type": "string"
                                },
                                "vlan_id": {
                                    "type": "string"
                                },
                                "vlan_type": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "vlan_type",
                                "type",
                                "vlan_id"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "201": {
                        "description": "Vlan has been added"
                    },
                    "406": {
                        "description": "Error from backend server"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Create a Vlan",
                "tags": [
                    "network"
                ]
            }
        },
        "/network/vlan_type": {
            "delete": {
                "description": "Delete a Vlan Type",
                "operationId": "deleteNetworkVlanType",
                "parameters": [
                    {
                        "description": "Delete a Vlan Type",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "id": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "id"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Vlan Type has been deleted"
                    },
                    "403": {
                        "description": "Permission issue"
                    },
                    "404": {
                        "description": "Vlan Type not found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Delete a Vlan Type",
                "tags": [
                    "network"
                ]
            },
            "get": {
                "description": "Returns a list of Vlan Types",
                "operationId": "getNetworkVlanType",
                "parameters": [
                    {
                        "default": 1,
                        "description": "page requested",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 1000 entries is the maximum allowed value",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "collectionFormat": "csv",
                        "default": [
                            "id"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "by default all the fields are returned but if a subset is required, list all the ones that should be included in the response",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "fields",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Vlan Types list",
                        "schema": {
                            "items": {
                                "properties": {
                                    "created": {
                                        "type": "string"
                                    },
                                    "created_by": {
                                        "type": "string"
                                    },
                                    "id": {
                                        "type": "string"
                                    },
                                    "name": {
                                        "type": "string"
                                    },
                                    "type": {
                                        "enum": [
                                            [
                                                "u'untagged'",
                                                "u'tagged'"
                                            ]
                                        ],
                                        "type": "string"
                                    },
                                    "updated": {
                                        "type": "string"
                                    },
                                    "updated_by": {
                                        "type": "string"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "403": {
                        "description": "not authorized to access"
                    },
                    "404": {
                        "description": "no Vlan Types found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get a list of Vlan Types",
                "tags": [
                    "network"
                ]
            },
            "post": {
                "description": "Create a Vlan Type",
                "operationId": "postNetworkVlanType",
                "parameters": [
                    {
                        "description": "Create a Vlan Type",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "name": {
                                    "type": "string"
                                },
                                "type": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "name",
                                "type"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "201": {
                        "description": "Vlan Type has been added"
                    },
                    "406": {
                        "description": "Error from backend server"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Create a Vlan Type",
                "tags": [
                    "network"
                ]
            },
            "put": {
                "description": "Edit a Vlan Type ",
                "operationId": "putNetworkVlanType",
                "parameters": [
                    {
                        "description": "Updat a Vlan Type",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "id": {
                                    "type": "string"
                                },
                                "name": {
                                    "type": "string"
                                },
                                "type": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "id"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Vlan Type has been updated"
                    },
                    "400": {
                        "description": "Generic Error"
                    },
                    "404": {
                        "description": "Vlan Type  was not found"
                    },
                    "406": {
                        "description": "Error from backend server"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Edit a Vlan Type ",
                "tags": [
                    "network"
                ]
            }
        },
        "/network_operator": {
            "get": {
                "description": "Returns a list of network operators",
                "operationId": "getNetworkOperator",
                "parameters": [
                    {
                        "default": 1,
                        "description": "page requested",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 1000 entries is the maximum allowed value",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "collectionFormat": "csv",
                        "default": [
                            "id"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "by default all the fields are returned but if a subset is required, list all the ones that should be included in the response",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "fields",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "network operator list",
                        "schema": {
                            "items": {
                                "properties": {
                                    "created": {
                                        "type": "string"
                                    },
                                    "description": {
                                        "type": "string"
                                    },
                                    "id": {
                                        "type": "string"
                                    },
                                    "name": {
                                        "type": "string"
                                    },
                                    "updated": {
                                        "type": "string"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "403": {
                        "description": "not authorized to access"
                    },
                    "404": {
                        "description": "no network operators records found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get a list of network operators",
                "tags": [
                    "network operator"
                ]
            }
        },
        "/object": {
            "delete": {
                "description": "Delete an Object",
                "operationId": "deleteObject",
                "parameters": [
                    {
                        "description": "deleted user settings record",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "id": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "id"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Object has been deleted"
                    },
                    "404": {
                        "description": "Object not found"
                    },
                    "406": {
                        "description": "internal error"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Delete an Object",
                "tags": [
                    "coverage"
                ]
            },
            "get": {
                "description": "Returns a list of objects",
                "operationId": "getObject",
                "parameters": [
                    {
                        "description": "object IP Address",
                        "in": "query",
                        "name": "ip_address",
                        "type": "string"
                    },
                    {
                        "default": 1,
                        "description": "page requested",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 1000 entries is the maximum allowed value",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "collectionFormat": "csv",
                        "default": [
                            "id"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "by default all the fields are returned but if a subset is required, list all the ones that should be included in the response",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "fields",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "objects list",
                        "schema": {
                            "properties": {
                                "data": {
                                    "items": {
                                        "$ref": "#/definitions/Object"
                                    },
                                    "type": "array"
                                },
                                "message": {
                                    "type": "string"
                                }
                            },
                            "type": "object"
                        }
                    },
                    "403": {
                        "$ref": "#/responses/403Forbidden"
                    },
                    "404": {
                        "$ref": "#/responses/404NotFound"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get a list of objects",
                "tags": [
                    "object"
                ]
            },
            "post": {
                "description": "Create an object",
                "operationId": "postObject",
                "parameters": [
                    {
                        "description": "created object",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "active_from": {
                                    "type": "string"
                                },
                                "apartment_number": {
                                    "type": "string"
                                },
                                "build_status": {
                                    "type": "string"
                                },
                                "building": {
                                    "type": "string"
                                },
                                "city": {
                                    "type": "string"
                                },
                                "class_code": {
                                    "type": "string"
                                },
                                "homedrop_price": {
                                    "type": "string"
                                },
                                "homedrop_status": {
                                    "type": "string"
                                },
                                "include_in_sdr": {
                                    "type": "string"
                                },
                                "latitude": {
                                    "type": "string"
                                },
                                "longitude": {
                                    "type": "string"
                                },
                                "manual_provisioning": {
                                    "type": "string"
                                },
                                "note": {
                                    "type": "string"
                                },
                                "object_group": {
                                    "type": "string"
                                },
                                "object_number": {
                                    "type": "string"
                                },
                                "object_type": {
                                    "type": "string"
                                },
                                "organization": {
                                    "type": "string"
                                },
                                "port": {
                                    "type": "string"
                                },
                                "postal_code": {
                                    "type": "string"
                                },
                                "province": {
                                    "type": "string"
                                },
                                "public_note": {
                                    "type": "string"
                                },
                                "status": {
                                    "type": "string"
                                },
                                "street": {
                                    "type": "string"
                                },
                                "street_number": {
                                    "type": "string"
                                },
                                "survey_result": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "manual_provisioning",
                                "object_type",
                                "object_number",
                                "city",
                                "object_group"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "201": {
                        "description": "Object has been created",
                        "schema": {
                            "properties": {
                                "data": {
                                    "$ref": "#/definitions/Object"
                                },
                                "message": {
                                    "type": "string"
                                }
                            },
                            "type": "object"
                        }
                    },
                    "400": {
                        "$ref": "#/responses/400BadRequest"
                    },
                    "404": {
                        "$ref": "#/responses/404NotFound"
                    },
                    "406": {
                        "$ref": "#/responses/406NotAcceptable"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Create an object",
                "tags": [
                    "object"
                ]
            },
            "put": {
                "description": "Update the object with a specific id, if exists",
                "operationId": "putObject",
                "parameters": [
                    {
                        "description": "updated object",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "active_from": {
                                    "type": "string"
                                },
                                "apartment_number": {
                                    "type": "string"
                                },
                                "build_status": {
                                    "type": "string"
                                },
                                "building": {
                                    "type": "string"
                                },
                                "city": {
                                    "type": "string"
                                },
                                "class_code": {
                                    "type": "string"
                                },
                                "homedrop_price": {
                                    "type": "string"
                                },
                                "homedrop_status": {
                                    "type": "string"
                                },
                                "id": {
                                    "type": "string"
                                },
                                "include_in_sdr": {
                                    "type": "string"
                                },
                                "latitude": {
                                    "type": "string"
                                },
                                "longitude": {
                                    "type": "string"
                                },
                                "manual_provisioning": {
                                    "type": "string"
                                },
                                "note": {
                                    "type": "string"
                                },
                                "object_group": {
                                    "type": "string"
                                },
                                "object_type": {
                                    "type": "string"
                                },
                                "organization": {
                                    "type": "string"
                                },
                                "port": {
                                    "type": "string"
                                },
                                "postal_code": {
                                    "type": "string"
                                },
                                "province": {
                                    "type": "string"
                                },
                                "public_note": {
                                    "type": "string"
                                },
                                "status": {
                                    "type": "string"
                                },
                                "street": {
                                    "type": "string"
                                },
                                "street_number": {
                                    "type": "string"
                                },
                                "survey_result": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "id"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Object has been updated",
                        "schema": {
                            "properties": {
                                "data": {
                                    "$ref": "#/definitions/Object"
                                },
                                "message": {
                                    "type": "string"
                                }
                            },
                            "type": "object"
                        }
                    },
                    "400": {
                        "$ref": "#/responses/400BadRequest"
                    },
                    "404": {
                        "$ref": "#/responses/404NotFound"
                    },
                    "406": {
                        "$ref": "#/responses/406NotAcceptable"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Update an object",
                "tags": [
                    "object"
                ]
            }
        },
        "/object/address": {
            "get": {
                "description": "Get network addresses associated with the object",
                "parameters": [
                    {
                        "description": "object number",
                        "in": "query",
                        "name": "object_number",
                        "type": "string"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "list of object IP address",
                        "schema": {
                            "items": {
                                "properties": {
                                    "address": {
                                        "type": "string"
                                    },
                                    "lease": {
                                        "type": "string"
                                    },
                                    "object_number": {
                                        "type": "string"
                                    },
                                    "vlan_id": {
                                        "type": "string"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "401": {
                        "description": "unknown object"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get network addresses associated with the object",
                "tags": [
                    "object"
                ]
            }
        },
        "/object/info": {
            "get": {
                "description": "Get information about the port where object is connected",
                "operationId": "getObjectInfo",
                "parameters": [
                    {
                        "description": "object number",
                        "in": "query",
                        "name": "number",
                        "type": "string"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Object info",
                        "schema": {
                            "items": {
                                "properties": {
                                    "cpe": {
                                        "properties": {
                                            "rx_power": {
                                                "type": "number"
                                            },
                                            "tx_power": {
                                                "type": "number"
                                            }
                                        },
                                        "type": "object"
                                    },
                                    "raw": {
                                        "type": "string"
                                    },
                                    "switch": {
                                        "properties": {
                                            "rx_power\"": {
                                                "type": "number"
                                            },
                                            "transfer_distance": {
                                                "type": "number"
                                            },
                                            "tx_power": {
                                                "type": "number"
                                            }
                                        },
                                        "type": "object"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "404": {
                        "description": "Object not found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get information about the port where object is connected",
                "tags": [
                    "object"
                ]
            }
        },
        "/object/map": {
            "get": {
                "description": "Get maps around an object",
                "parameters": [
                    {
                        "description": "object id",
                        "in": "query",
                        "name": "id",
                        "type": "string"
                    },
                    {
                        "description": "object number",
                        "in": "query",
                        "name": "number",
                        "type": "string"
                    },
                    {
                        "description": "map height in pixels (default 300)",
                        "in": "query",
                        "name": "height",
                        "type": "integer"
                    },
                    {
                        "description": "map width in pixels (default 600)",
                        "in": "query",
                        "name": "width",
                        "type": "integer"
                    }
                ],
                "produces": [
                    "application/png"
                ],
                "responses": {
                    "200": {
                        "description": "maps image"
                    },
                    "401": {
                        "description": "unknown object"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get maps around an object",
                "tags": [
                    "object"
                ]
            }
        },
        "/object_group": {
            "delete": {
                "description": "Delete a Object Group",
                "operationId": "deleteObjectGroup",
                "parameters": [
                    {
                        "description": "Delete a Object Group",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "id": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "id"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Object Group has been deleted"
                    },
                    "403": {
                        "description": "Permission issue"
                    },
                    "404": {
                        "description": "Object Group not found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Delete a Object Group",
                "tags": [
                    "network"
                ]
            },
            "get": {
                "description": "Returns a list of object groups",
                "operationId": "getObjectGroup",
                "parameters": [
                    {
                        "default": 1,
                        "description": "page requested",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 1000 entries is the maximum allowed value",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "collectionFormat": "csv",
                        "default": [
                            "id"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "by default all the fields are returned but if a subset is required, list all the ones that should be included in the response",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "fields",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "object group list",
                        "schema": {
                            "items": {
                                "properties": {
                                    "created": {
                                        "type": "string"
                                    },
                                    "email": {
                                        "type": "string"
                                    },
                                    "id": {
                                        "type": "string"
                                    },
                                    "manual_provisioning": {
                                        "type": "string"
                                    },
                                    "name": {
                                        "type": "string"
                                    },
                                    "network_operator": {
                                        "type": "string"
                                    },
                                    "portal_url": {
                                        "type": "string"
                                    },
                                    "service_providers": {
                                        "type": "string"
                                    },
                                    "service_types": {
                                        "type": "string"
                                    },
                                    "updated": {
                                        "type": "string"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "403": {
                        "description": "not authorized to access"
                    },
                    "404": {
                        "description": "no object groups found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get a list of object groups",
                "tags": [
                    "network operator"
                ]
            },
            "post": {
                "description": "Create a Object Group",
                "operationId": "postObjectGroup",
                "parameters": [
                    {
                        "description": "Create a Object Group",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "email": {
                                    "type": "string"
                                },
                                "manual_provisioning": {
                                    "type": "string"
                                },
                                "name": {
                                    "type": "string"
                                },
                                "network_operator": {
                                    "type": "string"
                                },
                                "portal_url": {
                                    "type": "string"
                                },
                                "service_providers": {
                                    "type": "string"
                                },
                                "service_types": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "manual_provisioning",
                                "name",
                                "network_operator"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "201": {
                        "description": "Object Group has been added"
                    },
                    "406": {
                        "description": "Error from backend server"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Create a Object Group",
                "tags": [
                    "network"
                ]
            },
            "put": {
                "description": "Edit a Object Group",
                "operationId": "putObjectGroup",
                "parameters": [
                    {
                        "description": "Update Object Group",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "email": {
                                    "type": "string"
                                },
                                "id": {
                                    "type": "string"
                                },
                                "manual_provisioning": {
                                    "type": "string"
                                },
                                "name": {
                                    "type": "string"
                                },
                                "network_operator": {
                                    "type": "string"
                                },
                                "portal_url": {
                                    "type": "string"
                                },
                                "service_providers": {
                                    "type": "string"
                                },
                                "service_types": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "id"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Object Group has been updated"
                    },
                    "400": {
                        "description": "Generic Error"
                    },
                    "404": {
                        "description": "Object Group was not found"
                    },
                    "406": {
                        "description": "Error from backend server"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Edit a Object Group",
                "tags": [
                    "network"
                ]
            }
        },
        "/order": {
            "get": {
                "description": "Returns a list of orders",
                "operationId": "getOrder",
                "parameters": [
                    {
                        "default": 1,
                        "description": "page requested",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 1000 entries is the maximum allowed value",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "collectionFormat": "csv",
                        "default": [
                            "id"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "by default all the fields are returned but if a subset is required, list all the ones that should be included in the response",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "fields",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "orders list",
                        "schema": {
                            "properties": {
                                "data": {
                                    "items": {
                                        "$ref": "#/definitions/Order"
                                    },
                                    "type": "array"
                                }
                            },
                            "type": "object"
                        }
                    },
                    "404": {
                        "$ref": "#/responses/404NotFound"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get a list of orders",
                "tags": [
                    "order"
                ]
            },
            "post": {
                "description": "Create a new order. If object is not provided the order will be created in state Backlog.",
                "operationId": "postOrder",
                "parameters": [
                    {
                        "description": "order to be added",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "customer": {
                                    "type": "string"
                                },
                                "from_date": {
                                    "type": "string"
                                },
                                "object": {
                                    "type": "string"
                                },
                                "operator_order_number": {
                                    "type": "string"
                                },
                                "price": {
                                    "type": "string"
                                },
                                "provider_order_number": {
                                    "type": "string"
                                },
                                "sales_lead": {
                                    "type": "string"
                                },
                                "service": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "service",
                                "from_date",
                                "customer"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "201": {
                        "description": "Order created",
                        "schema": {
                            "properties": {
                                "data": {
                                    "$ref": "#/definitions/Order"
                                },
                                "message": {
                                    "type": "string"
                                }
                            },
                            "type": "object"
                        }
                    },
                    "404": {
                        "$ref": "#/responses/404NotFound"
                    },
                    "406": {
                        "$ref": "#/responses/406NotAcceptable"
                    },
                    "409": {
                        "$ref": "#/responses/409Conflict"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Create a new order",
                "tags": [
                    "order"
                ]
            },
            "put": {
                "description": "Update an order",
                "operationId": "putOrder",
                "parameters": [
                    {
                        "description": "order to be updated",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "customer": {
                                    "type": "string"
                                },
                                "from_date": {
                                    "type": "string"
                                },
                                "id": {
                                    "type": "string"
                                },
                                "is_paid": {
                                    "type": "string"
                                },
                                "object": {
                                    "type": "string"
                                },
                                "operator_order_number": {
                                    "type": "string"
                                },
                                "price": {
                                    "type": "string"
                                },
                                "provider_order_number": {
                                    "type": "string"
                                },
                                "service": {
                                    "type": "string"
                                },
                                "state": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "id",
                                "service",
                                "from_date",
                                "customer"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "order updated",
                        "schema": {
                            "properties": {
                                "data": {
                                    "$ref": "#/definitions/Order"
                                },
                                "message": {
                                    "type": "string"
                                }
                            },
                            "type": "object"
                        }
                    },
                    "400": {
                        "$ref": "#/responses/400BadRequest"
                    },
                    "401": {
                        "$ref": "#/responses/401Unauthorized"
                    },
                    "406": {
                        "$ref": "#/responses/406NotAcceptable"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Update an order",
                "tags": [
                    "order"
                ]
            }
        },
        "/place": {
            "get": {
                "description": "Get Customer places",
                "operationId": "getPlace",
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Places associated to the customer",
                        "schema": {
                            "properties": {
                                "data": {
                                    "items": {
                                        "$ref": "#/definitions/Place"
                                    },
                                    "type": "array"
                                }
                            },
                            "type": "object"
                        }
                    },
                    "404": {
                        "$ref": "#/responses/404NotFound"
                    },
                    "406": {
                        "$ref": "#/responses/406NotAcceptable"
                    }
                },
                "summary": "Get Customer places",
                "tags": [
                    "customer"
                ]
            }
        },
        "/port": {
            "get": {
                "description": "Returns a list of network switch ports",
                "parameters": [
                    {
                        "default": 1,
                        "description": "page requested",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 1000 entries is the maximum allowed value",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "collectionFormat": "csv",
                        "default": [
                            "id"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "by default all the fields are returned but if a subset is required, list all the ones that should be included in the response",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "fields",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "network operator list",
                        "schema": {
                            "properties": {
                                "data": {
                                    "items": {
                                        "properties": {
                                            "created": {
                                                "type": "string"
                                            },
                                            "id": {
                                                "type": "string"
                                            },
                                            "module_number": {
                                                "type": "string"
                                            },
                                            "module_offset": {
                                                "type": "string"
                                            },
                                            "network": {
                                                "type": "string"
                                            },
                                            "network_operator": {
                                                "type": "string"
                                            },
                                            "number": {
                                                "type": "string"
                                            },
                                            "site": {
                                                "type": "string"
                                            },
                                            "status": {
                                                "enum": [
                                                    [
                                                        "u'Active'",
                                                        "u'Broken'",
                                                        "u'Reserved'"
                                                    ]
                                                ],
                                                "type": "string"
                                            },
                                            "switch": {
                                                "type": "string"
                                            },
                                            "switch_name": {
                                                "type": "string"
                                            },
                                            "type": {
                                                "type": "string"
                                            },
                                            "updated": {
                                                "type": "string"
                                            }
                                        },
                                        "type": "object"
                                    },
                                    "type": "array"
                                }
                            },
                            "type": "object"
                        }
                    },
                    "403": {
                        "description": "not authorized to access"
                    },
                    "404": {
                        "description": "no network operators records found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get a list of network switch ports",
                "tags": [
                    "network"
                ]
            }
        },
        "/port/info": {
            "get": {
                "description": "Get information about the port",
                "operationId": "getPortInfo",
                "parameters": [
                    {
                        "description": "switch id or switch name",
                        "in": "query",
                        "name": "switch",
                        "type": "string"
                    },
                    {
                        "description": "port id or port name",
                        "in": "query",
                        "name": "port",
                        "type": "string"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Port information",
                        "schema": {
                            "properties": {
                                "data": {
                                    "properties": {
                                        "description": {
                                            "type": "string"
                                        },
                                        "in_discards": {
                                            "type": "number"
                                        },
                                        "in_errors": {
                                            "type": "number"
                                        },
                                        "in_nu_cast_pkts": {
                                            "type": "number"
                                        },
                                        "in_octets": {
                                            "type": "number"
                                        },
                                        "in_u_cast_pkts": {
                                            "type": "number"
                                        },
                                        "in_unknown_protos": {
                                            "type": "number"
                                        },
                                        "last_change": {
                                            "type": "number"
                                        },
                                        "link": {
                                            "type": "string"
                                        },
                                        "mtu": {
                                            "type": "number"
                                        },
                                        "name": {
                                            "type": "string"
                                        },
                                        "optical_bias_current": {
                                            "type": "number"
                                        },
                                        "optical_rx_power": {
                                            "type": "number"
                                        },
                                        "optical_temperature": {
                                            "type": "number"
                                        },
                                        "optical_tx_power": {
                                            "type": "number"
                                        },
                                        "optical_vendor_pn": {
                                            "type": "string"
                                        },
                                        "optical_vendor_sn": {
                                            "type": "string"
                                        },
                                        "optical_voltage": {
                                            "type": "number"
                                        },
                                        "out_discards": {
                                            "type": "number"
                                        },
                                        "out_errors": {
                                            "type": "number"
                                        },
                                        "out_nu_cast_pkts": {
                                            "type": "number"
                                        },
                                        "out_octets": {
                                            "type": "number"
                                        },
                                        "out_u_cast_pkts": {
                                            "type": "number"
                                        },
                                        "port": {
                                            "type": "string"
                                        },
                                        "remote_port_id": {
                                            "type": "string"
                                        },
                                        "remote_sys_name": {
                                            "type": "string"
                                        },
                                        "speed": {
                                            "type": "number"
                                        },
                                        "state": {
                                            "type": "string"
                                        },
                                        "status": {
                                            "type": "string"
                                        },
                                        "switch": {
                                            "type": "string"
                                        },
                                        "timestamp": {
                                            "type": "string"
                                        },
                                        "type": {
                                            "type": "string"
                                        }
                                    },
                                    "type": "object"
                                }
                            },
                            "type": "object"
                        }
                    },
                    "404": {
                        "description": "Port unknown"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get information about the port",
                "tags": [
                    "network"
                ]
            }
        },
        "/port_error": {
            "get": {
                "description": "Returns a list of port error.",
                "parameters": [
                    {
                        "default": 1,
                        "description": "page requested",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 1000 entries is the maximum allowed value",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "collectionFormat": "csv",
                        "default": [
                            "id"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "by default all the fields are returned but if a subset is required, list all the ones that should be included in the response",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "fields",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "port error list",
                        "schema": {
                            "items": {
                                "properties": {
                                    "errors": {
                                        "type": "string"
                                    },
                                    "id": {
                                        "type": "string"
                                    },
                                    "last_seen": {
                                        "type": "string"
                                    },
                                    "network": {
                                        "type": "string"
                                    },
                                    "network_operator": {
                                        "type": "string"
                                    },
                                    "occurrences": {
                                        "type": "string"
                                    },
                                    "port": {
                                        "type": "string"
                                    },
                                    "port_name": {
                                        "type": "string"
                                    },
                                    "remote": {
                                        "type": "string"
                                    },
                                    "switch": {
                                        "type": "string"
                                    },
                                    "switch_name": {
                                        "type": "string"
                                    },
                                    "updated": {
                                        "type": "string"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "403": {
                        "description": "not authorized to access"
                    },
                    "404": {
                        "description": "no port error found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get port errors reported in the last week",
                "tags": [
                    "network"
                ]
            }
        },
        "/postcode": {
            "get": {
                "description": "Returns a list of addresses bind on the Postal Code",
                "operationId": "getPostcode",
                "parameters": [
                    {
                        "description": "UK Postal Code",
                        "in": "query",
                        "name": "postcode",
                        "type": "string"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Addesses list",
                        "schema": {
                            "items": {
                                "properties": {
                                    "administrative_county": {
                                        "type": "string"
                                    },
                                    "building_name": {
                                        "type": "string"
                                    },
                                    "building_number": {
                                        "type": "string"
                                    },
                                    "country": {
                                        "type": "string"
                                    },
                                    "county": {
                                        "type": "string"
                                    },
                                    "delivery_point_suffix": {
                                        "type": "string"
                                    },
                                    "department_name": {
                                        "type": "string"
                                    },
                                    "dependant_locality": {
                                        "type": "string"
                                    },
                                    "dependant_thoroughfare": {
                                        "type": "string"
                                    },
                                    "district": {
                                        "type": "string"
                                    },
                                    "double_dependant_locality": {
                                        "type": "string"
                                    },
                                    "eastings": {
                                        "type": "string"
                                    },
                                    "latitude": {
                                        "type": "string"
                                    },
                                    "line_1": {
                                        "type": "string"
                                    },
                                    "line_2": {
                                        "type": "string"
                                    },
                                    "line_3": {
                                        "type": "string"
                                    },
                                    "longitude": {
                                        "type": "string"
                                    },
                                    "northings": {
                                        "type": "string"
                                    },
                                    "organisation_name": {
                                        "type": "string"
                                    },
                                    "po_box": {
                                        "type": "string"
                                    },
                                    "post_town": {
                                        "type": "string"
                                    },
                                    "postal_county": {
                                        "type": "string"
                                    },
                                    "postcode": {
                                        "type": "string"
                                    },
                                    "postcode_inward": {
                                        "type": "string"
                                    },
                                    "postcode_outward": {
                                        "type": "string"
                                    },
                                    "postcode_type": {
                                        "type": "string"
                                    },
                                    "premise": {
                                        "type": "string"
                                    },
                                    "su_organisation_indicator": {
                                        "type": "string"
                                    },
                                    "sub_building_name": {
                                        "type": "string"
                                    },
                                    "thoroughfare": {
                                        "type": "string"
                                    },
                                    "traditional_county": {
                                        "type": "string"
                                    },
                                    "udprn": {
                                        "type": "string"
                                    },
                                    "umprn": {
                                        "type": "string"
                                    },
                                    "ward": {
                                        "type": "string"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "400": {
                        "description": "Generic error"
                    },
                    "404": {
                        "description": "Postal code not found"
                    },
                    "406": {
                        "description": "Postal code not valid"
                    },
                    "504": {
                        "description": "External service error"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get a list of addresses bind on the Postal Code",
                "tags": [
                    "coverage"
                ]
            }
        },
        "/report": {
            "get": {
                "description": "Get the list of available reports",
                "operationId": "getReports",
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "the list of available reports"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get the list of available reports",
                "tags": [
                    "report"
                ]
            }
        },
        "/report/active_orders": {
            "get": {
                "description": "List of all the active orders",
                "parameters": [
                    {
                        "description": "limit the scope only to the statistics that belong to the id of the provided network_operator",
                        "in": "query",
                        "name": "network_operator",
                        "type": "string"
                    },
                    {
                        "description": "limit the scope only to the statistics that belong to the id of the provided service_provider.",
                        "in": "query",
                        "name": "service_provider",
                        "type": "string"
                    },
                    {
                        "default": 1,
                        "description": "requested page",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 0 to disable the limit and gives back all the entries",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "default": [
                            "created"
                        ],
                        "description": "fields we want items to be order by ; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "daily statistics",
                        "schema": {
                            "items": {
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "401": {
                        "description": "unknown network_operator"
                    },
                    "402": {
                        "description": "unknown service_provider"
                    },
                    "404": {
                        "description": "no record found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Report about activer order",
                "tags": [
                    "report"
                ]
            }
        },
        "/report/api_log_statistics": {
            "get": {
                "description": "Api Log Statistics Report",
                "operationId": "getReportApiLogStatistics",
                "parameters": [
                    {
                        "default": 1,
                        "description": "requested page",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 0 to disable the limit and gives back all the entries",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "description": "start date and time in iso8601 format (i.e. 2000-05-22T00:00:00)",
                        "in": "query",
                        "name": "start",
                        "required": True,
                        "type": "string"
                    },
                    {
                        "description": "stop date and time in iso8601 format (i.e. 2010-05-22T00:00:00)",
                        "in": "query",
                        "name": "stop",
                        "required": True,
                        "type": "string"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "default": [
                            "client_ip",
                            "name",
                            "resource",
                            "method"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Api Log Statistics",
                        "schema": {
                            "items": {
                                "properties": {
                                    "avg": {
                                        "type": "string"
                                    },
                                    "client_ip": {
                                        "type": "string"
                                    },
                                    "count": {
                                        "type": "string"
                                    },
                                    "max": {
                                        "type": "string"
                                    },
                                    "method": {
                                        "type": "string"
                                    },
                                    "min": {
                                        "type": "string"
                                    },
                                    "name": {
                                        "type": "string"
                                    },
                                    "resource": {
                                        "type": "string"
                                    },
                                    "role": {
                                        "type": "string"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "404": {
                        "description": "no record found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Api Log Statistics Report",
                "tags": [
                    "report"
                ]
            }
        },
        "/report/arps": {
            "get": {
                "description": "List of all the active orders",
                "operationId": "getReportArps",
                "parameters": [
                    {
                        "description": "limit the scope only to the statistics that belong to the id of the provided network_operator",
                        "in": "query",
                        "name": "network_operator",
                        "type": "string"
                    },
                    {
                        "description": "date in iso8601 format (i.e. 2000-05-22T00:00:00) of the desired data",
                        "in": "query",
                        "name": "date",
                        "type": "string"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "daily statistics",
                        "schema": {
                            "items": {
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "401": {
                        "description": "unknown network_operator"
                    },
                    "402": {
                        "description": "unknown service_provider"
                    },
                    "404": {
                        "description": "no record found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Report about Average Revenue per Service (ARPS)",
                "tags": [
                    "report"
                ]
            }
        },
        "/report/check_switch_ports": {
            "get": {
                "description": "Check if some switches have less Access port than expected",
                "operationId": "getReportCheckSwitchPorts",
                "produces": [
                    "application/json",
                    "application/png"
                ],
                "responses": {
                    "200": {
                        "description": "Check switch port report"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Check Switch Port",
                "tags": [
                    "report"
                ]
            }
        },
        "/report/interface_utilization": {
            "get": {
                "description": "Report on interface Utilization in either json or graphic (png) format",
                "operationId": "getReportInterfaceUtilization",
                "parameters": [
                    {
                        "description": "interface name (get list of interfaces  with get to network/interfaces)",
                        "in": "query",
                        "name": "name",
                        "required": True,
                        "type": "string"
                    },
                    {
                        "description": "the format of the report; available format are json and png (default json)",
                        "in": "query",
                        "name": "format",
                        "type": "string"
                    },
                    {
                        "description": "starting time in unix at command format (default e-30min)",
                        "in": "query",
                        "name": "start",
                        "type": "string"
                    },
                    {
                        "description": "ending time in unix at command format (default now)",
                        "in": "query",
                        "name": "end",
                        "type": "string"
                    },
                    {
                        "description": "sampling interval in seconds (default 3600)",
                        "in": "query",
                        "name": "resolution",
                        "type": "integer"
                    },
                    {
                        "description": "interface nominal speed in bps; it's used to scale the graph (default 1G)",
                        "in": "query",
                        "name": "speed",
                        "type": "integer"
                    },
                    {
                        "description": "the label for ingress traffic (default in)",
                        "in": "query",
                        "name": "in_label",
                        "type": "string"
                    },
                    {
                        "description": "the label for egress traffic (default out)",
                        "in": "query",
                        "name": "out_label",
                        "type": "string"
                    }
                ],
                "produces": [
                    "application/json",
                    "application/png"
                ],
                "responses": {
                    "200": {
                        "description": "Interface utilization"
                    },
                    "401": {
                        "description": "Unknown interface"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Report on interface Utilization",
                "tags": [
                    "report"
                ]
            }
        },
        "/report/network_availability": {
            "get": {
                "description": "Report on network availability. Return a json.<br/><br/>The availability is calculated for a reference period defined by a month in a year.<br/>TSH = Total Service Hours<br/>DH = Downtime Hours<br/>AV = Availability  (%)<br/>AV = (TSH - DH) / TSH * 100",
                "operationId": "getReportNetworkAvailability",
                "parameters": [
                    {
                        "description": "month used to calculate the network availability",
                        "in": "query",
                        "name": "month",
                        "type": "integer"
                    },
                    {
                        "description": "year used to calculate the network availability",
                        "in": "query",
                        "name": "year",
                        "type": "integer"
                    },
                    {
                        "description": "network operator. You can use id or name. Just accesible for Admin.",
                        "in": "query",
                        "name": "network_operator",
                        "type": "string"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "objects with no active orders",
                        "schema": {
                            "properties": {
                                "assigned_availability": {
                                    "type": "integer"
                                },
                                "assigned_downtime_hours": {
                                    "type": "integer"
                                },
                                "network_operator": {
                                    "type": "string"
                                },
                                "network_operator_name": {
                                    "type": "string"
                                },
                                "total_availability": {
                                    "type": "integer"
                                },
                                "total_downtime_hours": {
                                    "type": "integer"
                                },
                                "total_service_hours": {
                                    "type": "integer"
                                }
                            },
                            "type": "object"
                        }
                    },
                    "404": {
                        "description": "network operator or data not found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Report on network availability.",
                "tags": [
                    "report"
                ]
            }
        },
        "/report/node_statistics": {
            "get": {
                "description": "Report on network node availability and health either json or graphic (png) format",
                "operationId": "getNodeStatistics",
                "parameters": [
                    {
                        "description": "interface name (get list of interfaces  with get to network/interfaces)",
                        "in": "query",
                        "name": "name",
                        "required": True,
                        "type": "string"
                    },
                    {
                        "description": "the format of the report; available format are json and png (default json)",
                        "in": "query",
                        "name": "format",
                        "type": "string"
                    },
                    {
                        "description": "starting time in unix at command format (default e-30min)",
                        "in": "query",
                        "name": "start",
                        "type": "string"
                    },
                    {
                        "description": "ending time in unix at command format (default now)",
                        "in": "query",
                        "name": "end",
                        "type": "string"
                    },
                    {
                        "description": "sampling interval in seconds (default 3600)",
                        "in": "query",
                        "name": "resolution",
                        "type": "integer"
                    }
                ],
                "produces": [
                    "application/json",
                    "application/png"
                ],
                "responses": {
                    "200": {
                        "description": "node statistics"
                    },
                    "401": {
                        "description": "unknown node"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Report on network node statistics",
                "tags": [
                    "report"
                ]
            }
        },
        "/report/object_connections": {
            "get": {
                "description": "List the objects and where they are connected to",
                "operationId": "getReportObjectConnections",
                "parameters": [
                    {
                        "description": "limit the scope only to the statistics that belong to the id of the provided network_operator",
                        "in": "query",
                        "name": "network_operator",
                        "type": "string"
                    },
                    {
                        "description": "date in iso8601 format (i.e. 2000-05-22T00:00:00) of the desired data",
                        "in": "query",
                        "name": "date",
                        "type": "string"
                    },
                    {
                        "default": 1,
                        "description": "requested page",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 0 to disable the limit and gives back all the entries",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "default": [
                            "created"
                        ],
                        "description": "fields we want items to be order by ; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "default": "",
                        "description": "query",
                        "in": "query",
                        "name": "q",
                        "type": "string"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "object list",
                        "schema": {
                            "items": {
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "401": {
                        "description": "unknown network_operator"
                    },
                    "404": {
                        "description": "no record found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Report about objects connection",
                "tags": [
                    "report"
                ]
            }
        },
        "/report/object_noservice": {
            "get": {
                "description": "Report on statistics splitted by Object Group, Service Provider, Service Type and Customer Type",
                "operationId": "getReportObjectNoService",
                "parameters": [
                    {
                        "description": "limit the scope only to the statistics that belong to the id of the provided network_operator",
                        "in": "query",
                        "name": "network_operator",
                        "type": "string"
                    },
                    {
                        "description": "limit the scope only to the statistics that belong to the id of the provided service_provider.",
                        "in": "query",
                        "name": "service_provider",
                        "type": "string"
                    },
                    {
                        "default": 1,
                        "description": "requested page",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 0 to disable the limit and gives back all the entries",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "objects with no active orders",
                        "schema": {
                            "items": {
                                "properties": {
                                    "active_from": {
                                        "type": "string"
                                    },
                                    "apartment_number": {
                                        "type": "string"
                                    },
                                    "area": {
                                        "type": "string"
                                    },
                                    "city": {
                                        "type": "string"
                                    },
                                    "created": {
                                        "type": "string"
                                    },
                                    "id": {
                                        "type": "string"
                                    },
                                    "latitude": {
                                        "type": "string"
                                    },
                                    "longitude": {
                                        "type": "string"
                                    },
                                    "manual_provisioning": {
                                        "type": "string"
                                    },
                                    "network_operator": {
                                        "type": "string"
                                    },
                                    "note": {
                                        "type": "string"
                                    },
                                    "object_group": {
                                        "type": "string"
                                    },
                                    "object_number": {
                                        "type": "string"
                                    },
                                    "object_type": {
                                        "type": "string"
                                    },
                                    "postal_code": {
                                        "type": "string"
                                    },
                                    "province": {
                                        "type": "string"
                                    },
                                    "provisioning_status": {
                                        "type": "string"
                                    },
                                    "public_note": {
                                        "type": "string"
                                    },
                                    "status": {
                                        "type": "string"
                                    },
                                    "street": {
                                        "type": "string"
                                    },
                                    "street_number": {
                                        "type": "string"
                                    },
                                    "updated": {
                                        "type": "string"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "401": {
                        "description": "unknown network_operator"
                    },
                    "402": {
                        "description": "unknown service_provider"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Report on statistics",
                "tags": [
                    "report"
                ]
            }
        },
        "/report/object_statistics": {
            "get": {
                "description": "Report on objects state splitted by group",
                "operationId": "getReportObjectStatistics",
                "parameters": [
                    {
                        "description": "limit the scope only to the object that belong to the id of network operator provided",
                        "in": "query",
                        "name": "network_operator",
                        "type": "string"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "statistics of objects splitted by status and group"
                    },
                    "401": {
                        "description": "unknown netowrk operator"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Report on objects statistics",
                "tags": [
                    "report"
                ]
            }
        },
        "/report/object_traffic": {
            "get": {
                "description": "Report on objects state splitted by group",
                "operationId": "getReportObjectTraffic",
                "parameters": [
                    {
                        "description": "object_id or object_number",
                        "in": "query",
                        "name": "object",
                        "type": "string"
                    },
                    {
                        "description": "start date in ISO format",
                        "in": "query",
                        "name": "start",
                        "type": "string"
                    },
                    {
                        "description": "days, weeks, months",
                        "in": "query",
                        "name": "type",
                        "type": "string"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Object traffic"
                    },
                    "400": {
                        "description": "Unknown object"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Report on objects traffic usage",
                "tags": [
                    "report"
                ]
            }
        },
        "/report/order_statistics": {
            "get": {
                "description": "Statistics on status of the orders created in the last year splitted by months",
                "operationId": "getReportOrderStatistics",
                "parameters": [
                    {
                        "description": "limit the scope only to the statistics that belong to the id of the provided network_operator",
                        "in": "query",
                        "name": "network_operator",
                        "type": "string"
                    },
                    {
                        "description": "limit the scope only to the statistics that belong to the id of the provided service_provider.",
                        "in": "query",
                        "name": "service_provider",
                        "type": "string"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "daily statistics",
                        "schema": {
                            "items": {
                                "properties": {
                                    "YYYY-MM": {
                                        "properties": {
                                            "Active": {
                                                "type": "integer"
                                            },
                                            "Awaiting activation": {
                                                "type": "integer"
                                            },
                                            "Backlog Completed": {
                                                "type": "integer"
                                            },
                                            "Backlog Created": {
                                                "type": "integer"
                                            },
                                            "Cancelled": {
                                                "type": "integer"
                                            },
                                            "Shelved": {
                                                "type": "integer"
                                            }
                                        },
                                        "type": "object"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "401": {
                        "description": "unknown network_operator"
                    },
                    "402": {
                        "description": "unknown service_provider"
                    },
                    "404": {
                        "description": "no record found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Order statistics",
                "tags": [
                    "report"
                ]
            }
        },
        "/report/real_customer_churn_rate": {
            "get": {
                "description": "Real Customer Churn Rate: percentage of customers that terminate their subscriptions in a given period <br/>and at the end of that period do not have a subscription",
                "operationId": "getReportRealChurnRate",
                "parameters": [
                    {
                        "description": "Start date in ISO format",
                        "in": "query",
                        "name": "start_date",
                        "type": "string"
                    },
                    {
                        "description": "End date in ISO format",
                        "in": "query",
                        "name": "end_date",
                        "type": "string"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Real Customer Churn Rate"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Real Customer Churn Rate",
                "tags": [
                    "report"
                ]
            }
        },
        "/report/real_object_churn_rate": {
            "get": {
                "description": "Real Customer Churn Rate: percentage of customers that terminate their subscriptions in a given period<br/>and at the end of that period do not have a subscription",
                "operationId": "getReportRealObjectChurnRate",
                "parameters": [
                    {
                        "description": "Start date in ISO format (yyyy-mm-dd)",
                        "in": "query",
                        "name": "start",
                        "type": "string"
                    },
                    {
                        "description": "End date in ISO format (yyyy-mm-dd)",
                        "in": "query",
                        "name": "end",
                        "type": "string"
                    },
                    {
                        "description": "Churn rate mode (all, inactive, provider, activated)",
                        "in": "query",
                        "name": "mode",
                        "type": "string"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Real Object Churn Rate"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Real Customer Churn Rate",
                "tags": [
                    "report"
                ]
            }
        },
        "/report/service_statistics": {
            "get": {
                "description": "Report on the number of active subscriptions present, splitted per service type, service provider and object group",
                "operationId": "getReportServiceStatistics",
                "parameters": [
                    {
                        "description": "limit the scope only to the services that belong to the id of the service provider provided",
                        "in": "query",
                        "name": "service_provider",
                        "type": "string"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Service statistics"
                    },
                    "401": {
                        "description": "Unknown Service Provider"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Report on service statistics",
                "tags": [
                    "report"
                ]
            }
        },
        "/report/speed_test": {
            "get": {
                "description": "Get the speed test report",
                "operationId": "getSpeedTest",
                "parameters": [
                    {
                        "description": "object name",
                        "in": "query",
                        "name": "object",
                        "required": True,
                        "type": "string"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "speed test"
                    },
                    "403": {
                        "description": "Permission error"
                    },
                    "404": {
                        "description": "Object not found"
                    },
                    "406": {
                        "description": "No data or procedure error"
                    },
                    "500": {
                        "description": "Internal server error"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get the speed test report",
                "tags": [
                    "report"
                ]
            }
        },
        "/report/stat": {
            "get": {
                "description": "Report on statistics splitted by Object Group, Service Provider, Service Type and Customer Type",
                "operationId": "getReportStat",
                "parameters": [
                    {
                        "description": "limit the scope only to the statistics that belong to the id of the provided network_operator",
                        "in": "query",
                        "name": "network_operator",
                        "type": "string"
                    },
                    {
                        "description": "limit the scope only to the statistics that belong to the id of the provided service_provider.",
                        "in": "query",
                        "name": "service_provider",
                        "type": "string"
                    },
                    {
                        "default": 1,
                        "description": "requested page",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 0 to disable the limit and gives back all the entries",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "description": "start date and time in iso8601 format (i.e. 2000-05-22T00:00:00)",
                        "in": "query",
                        "name": "start",
                        "type": "string"
                    },
                    {
                        "description": "stop date and time in iso8601 format (i.e. 2010-05-22T00:00:00)",
                        "in": "query",
                        "name": "stop",
                        "type": "string"
                    },
                    {
                        "default": True,
                        "description": "if true returns only last record of every day",
                        "in": "query",
                        "name": "last_of_the_day",
                        "type": "boolean"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "daily statistics",
                        "schema": {
                            "items": {
                                "properties": {
                                    "created": {
                                        "format": "date-time",
                                        "readOnly": True,
                                        "type": "string"
                                    },
                                    "name": {
                                        "readOnly": True,
                                        "type": "string"
                                    },
                                    "netowork_operator": {
                                        "readOnly": True,
                                        "type": "string"
                                    },
                                    "object_group": {
                                        "properties": {
                                            "OBJECT_GROUP_NAME": {
                                                "properties": {
                                                    "Deliverable": {
                                                        "type": "integer"
                                                    },
                                                    "In deployment": {
                                                        "type": "integer"
                                                    },
                                                    "active": {
                                                        "type": "integer"
                                                    },
                                                    "service_provider": {
                                                        "properties": {
                                                            "SERVICE_PROVIDER_NAME": {
                                                                "properties": {
                                                                    "active": {
                                                                        "properties": {
                                                                            "SERVICE_TYPE_NAME": {
                                                                                "type": "integer"
                                                                            }
                                                                        },
                                                                        "type": "object"
                                                                    },
                                                                    "customer_type": {
                                                                        "properties": {
                                                                            "Business": {
                                                                                "type": "integer"
                                                                            },
                                                                            "Education": {
                                                                                "type": "integer"
                                                                            },
                                                                            "Non Profit Organisation": {
                                                                                "type": "integer"
                                                                            },
                                                                            "Residential": {
                                                                                "type": "integer"
                                                                            }
                                                                        },
                                                                        "type": "object"
                                                                    },
                                                                    "id": {
                                                                        "type": "string"
                                                                    }
                                                                },
                                                                "readOnly": True,
                                                                "type": "object"
                                                            }
                                                        },
                                                        "readOnly": True,
                                                        "type": "object"
                                                    }
                                                },
                                                "readOnly": True,
                                                "type": "object"
                                            }
                                        },
                                        "readOnly": True,
                                        "type": "object"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "401": {
                        "description": "unknown network_operator"
                    },
                    "402": {
                        "description": "unknown service_provider"
                    },
                    "404": {
                        "description": "no record found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Report on statistics",
                "tags": [
                    "report"
                ]
            }
        },
        "/report/stat_object_group_object": {
            "get": {
                "description": "Object status split per object group, day or month and network operator",
                "parameters": [
                    {
                        "description": "limit the scope only to the statistics that belong to the id of the provided network_operator",
                        "in": "query",
                        "name": "network_operator",
                        "type": "string"
                    },
                    {
                        "description": "start date and time in iso8601 format (i.e. 2000-05-22T00:00:00). Default is 65 days ago.",
                        "in": "query",
                        "name": "start",
                        "type": "string"
                    },
                    {
                        "description": "stop date and time in iso8601 format (i.e. 2010-05-22T00:00:00). Default is now.",
                        "in": "query",
                        "name": "stop",
                        "type": "string"
                    },
                    {
                        "description": "daily or montly samples. Default is daily.",
                        "in": "query",
                        "name": "mode",
                        "type": "string"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "service type statistics",
                        "schema": {
                            "items": {
                                "properties": {
                                    "date": {
                                        "type": "string"
                                    },
                                    "network_operator": {
                                        "type": "string"
                                    },
                                    "network_operator.name": {
                                        "type": "string"
                                    },
                                    "object": {
                                        "properties": {
                                            "Deliverable": {
                                                "type": "integer"
                                            },
                                            "In deployment": {
                                                "type": "integer"
                                            },
                                            "Not deliverable": {
                                                "type": "integer"
                                            },
                                            "active": {
                                                "type": "integer"
                                            }
                                        },
                                        "type": "object"
                                    },
                                    "object_group.name": {
                                        "type": "string"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "401": {
                        "description": "unknown network_operator"
                    },
                    "404": {
                        "description": "no record found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Object status split per object group, day or month and network operator",
                "tags": [
                    "report"
                ]
            }
        },
        "/report/stat_object_service_type": {
            "get": {
                "description": "Object status, customer type and service types statistic split per day or month and network operator",
                "parameters": [
                    {
                        "description": "limit the scope only to the statistics that belong to the id of the provided network_operator",
                        "in": "query",
                        "name": "network_operator",
                        "type": "string"
                    },
                    {
                        "description": "start date and time in iso8601 format (i.e. 2000-05-22T00:00:00). Default is 65 days ago.",
                        "in": "query",
                        "name": "start",
                        "type": "string"
                    },
                    {
                        "description": "stop date and time in iso8601 format (i.e. 2010-05-22T00:00:00). Default is now.",
                        "in": "query",
                        "name": "stop",
                        "type": "string"
                    },
                    {
                        "description": "daily or montly samples. Default is daily.",
                        "in": "query",
                        "name": "mode",
                        "type": "string"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "service type statistics",
                        "schema": {
                            "items": {
                                "properties": {
                                    "customer": {
                                        "properties": {
                                            "Business": {
                                                "type": "integer"
                                            },
                                            "Education": {
                                                "type": "integer"
                                            },
                                            "Non Profit Organisation": {
                                                "type": "integer"
                                            },
                                            "Residential": {
                                                "type": "integer"
                                            }
                                        },
                                        "type": "object"
                                    },
                                    "date": {
                                        "type": "string"
                                    },
                                    "network_operator": {
                                        "type": "string"
                                    },
                                    "network_operator.name": {
                                        "type": "string"
                                    },
                                    "object": {
                                        "properties": {
                                            "Deliverable": {
                                                "type": "integer"
                                            },
                                            "In deployment": {
                                                "type": "integer"
                                            },
                                            "Not deliverable": {
                                                "type": "integer"
                                            },
                                            "active": {
                                                "type": "integer"
                                            }
                                        },
                                        "type": "object"
                                    },
                                    "service_type": {
                                        "properties": {
                                            "SERVICE_TYPE_NAME": {
                                                "type": "integer"
                                            }
                                        },
                                        "type": "object"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "401": {
                        "description": "unknown network_operator"
                    },
                    "404": {
                        "description": "no record found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Object status, customer type and service types statistic split per day or month and network operator",
                "tags": [
                    "report"
                ]
            }
        },
        "/report/stat_service_type_provider": {
            "get": {
                "description": "Report Service Type and Serice Provider Statistics split by Netowrk operator",
                "parameters": [
                    {
                        "description": "limit the scope only to the statistics that belong to the id of the provided network_operator",
                        "in": "query",
                        "name": "network_operator",
                        "type": "string"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "service type statistics",
                        "schema": {
                            "items": {
                                "properties": {
                                    "network_operator": {
                                        "type": "string"
                                    },
                                    "network_operator.name": {
                                        "type": "string"
                                    },
                                    "num_service_provider": {
                                        "type": "integer"
                                    },
                                    "service_type": {
                                        "properties": {
                                            "SERVICE_TYPE_NAME": {
                                                "type": "integer"
                                            }
                                        },
                                        "type": "object"
                                    },
                                    "total": {
                                        "type": "integer"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "401": {
                        "description": "unknown network_operator"
                    },
                    "404": {
                        "description": "no record found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Report Service Type and Serice Provider Statistics",
                "tags": [
                    "report"
                ]
            }
        },
        "/report/switch_statistics": {
            "get": {
                "description": "Number of Switch split per Network, Site, Model, Driver and Status",
                "operationId": "getReportSwitchStatistics",
                "parameters": [
                    {
                        "default": True,
                        "description": "if true split result by network",
                        "in": "query",
                        "name": "split_network",
                        "type": "boolean"
                    },
                    {
                        "default": True,
                        "description": "if true split result by node",
                        "in": "query",
                        "name": "split_site",
                        "type": "boolean"
                    },
                    {
                        "default": True,
                        "description": "if true split result by model",
                        "in": "query",
                        "name": "split_model",
                        "type": "boolean"
                    },
                    {
                        "default": True,
                        "description": "if true split result by driver",
                        "in": "query",
                        "name": "split_driver",
                        "type": "boolean"
                    },
                    {
                        "default": True,
                        "description": "if true split result by switch status",
                        "in": "query",
                        "name": "split_status",
                        "type": "boolean"
                    },
                    {
                        "default": True,
                        "description": "if true count only active switches",
                        "in": "query",
                        "name": "only_active",
                        "type": "boolean"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "switch statistics (some of the fields reported below are present ot not depending on the request)",
                        "schema": {
                            "items": {
                                "properties": {
                                    "driver": {
                                        "type": "string"
                                    },
                                    "model": {
                                        "type": "string"
                                    },
                                    "network": {
                                        "type": "string"
                                    },
                                    "network.name": {
                                        "type": "string"
                                    },
                                    "number_of_active_ports": {
                                        "type": "number"
                                    },
                                    "number_of_physical_switches": {
                                        "type": "number"
                                    },
                                    "number_of_ports": {
                                        "type": "number"
                                    },
                                    "number_of_switches": {
                                        "type": "number"
                                    },
                                    "site": {
                                        "type": "string"
                                    },
                                    "status": {
                                        "type": "string"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "404": {
                        "description": "no record found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Number of Switch split per Network, Site, Model, Driver and Status",
                "tags": [
                    "report"
                ]
            }
        },
        "/sales_lead": {
            "delete": {
                "description": "Delete a Sales Lead record. id must be provided.",
                "operationId": "deleteSalesLead",
                "parameters": [
                    {
                        "description": "deleted user settings record",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "id": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "id"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Sales Lead has been deleted"
                    },
                    "403": {
                        "description": "permission issue"
                    },
                    "404": {
                        "description": "Sales Lead not found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Delete a Sales Lead record",
                "tags": [
                    "coverage"
                ]
            },
            "get": {
                "description": "Returns a list of Sales Lead.",
                "operationId": "getSalesLead",
                "parameters": [
                    {
                        "default": 1,
                        "description": "page requested",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 1000 entries is the maximum allowed value",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "collectionFormat": "csv",
                        "default": [
                            "id"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "by default all the fields are returned but if a subset is required, list all the ones that should be included in the response",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "fields",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "zone record list",
                        "schema": {
                            "items": {
                                "properties": {
                                    "accept_survey_message": {
                                        "type": "string"
                                    },
                                    "address_verified": {
                                        "type": "string"
                                    },
                                    "allow_service_order": {
                                        "type": "string"
                                    },
                                    "apartment_number": {
                                        "type": "string"
                                    },
                                    "building": {
                                        "type": "string"
                                    },
                                    "bundle": {
                                        "type": "string"
                                    },
                                    "cancel_message": {
                                        "type": "string"
                                    },
                                    "city": {
                                        "type": "string"
                                    },
                                    "company_name": {
                                        "type": "string"
                                    },
                                    "country": {
                                        "type": "string"
                                    },
                                    "created": {
                                        "type": "string"
                                    },
                                    "customer": {
                                        "type": "string"
                                    },
                                    "customer_type": {
                                        "type": "string"
                                    },
                                    "earlystart_message": {
                                        "type": "string"
                                    },
                                    "email": {
                                        "type": "string"
                                    },
                                    "first_name": {
                                        "type": "string"
                                    },
                                    "home_drop": {
                                        "type": "string"
                                    },
                                    "homedrop": {
                                        "type": "string"
                                    },
                                    "homedrop_index": {
                                        "type": "string"
                                    },
                                    "homedrop_price": {
                                        "type": "string"
                                    },
                                    "id": {
                                        "type": "string"
                                    },
                                    "last_name": {
                                        "type": "string"
                                    },
                                    "lat": {
                                        "type": "string"
                                    },
                                    "lng": {
                                        "type": "string"
                                    },
                                    "manual_check": {
                                        "type": "string"
                                    },
                                    "manual_check_price": {
                                        "type": "string"
                                    },
                                    "mobile_number": {
                                        "type": "string"
                                    },
                                    "multiple_homedrop": {
                                        "type": "string"
                                    },
                                    "network_operator": {
                                        "type": "string"
                                    },
                                    "object": {
                                        "type": "string"
                                    },
                                    "object_group": {
                                        "type": "string"
                                    },
                                    "organization": {
                                        "type": "string"
                                    },
                                    "payment": {
                                        "type": "string"
                                    },
                                    "payment_tok": {
                                        "type": "string"
                                    },
                                    "phone_number": {
                                        "type": "string"
                                    },
                                    "position_precision": {
                                        "type": "string"
                                    },
                                    "postal_code": {
                                        "type": "string"
                                    },
                                    "province": {
                                        "type": "string"
                                    },
                                    "reject_survey_message": {
                                        "type": "string"
                                    },
                                    "sales_lead_number": {
                                        "type": "string"
                                    },
                                    "service": {
                                        "type": "string"
                                    },
                                    "service_price": {
                                        "type": "string"
                                    },
                                    "status": {
                                        "type": "string"
                                    },
                                    "street": {
                                        "type": "string"
                                    },
                                    "street_number": {
                                        "type": "string"
                                    },
                                    "updated": {
                                        "type": "string"
                                    },
                                    "url": {
                                        "type": "string"
                                    },
                                    "zone": {
                                        "type": "string"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "404": {
                        "description": "no zone records found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get Sales Leads",
                "tags": [
                    "coverage"
                ]
            },
            "post": {
                "description": "Create a new Sales Lead.",
                "operationId": "postSalesLead",
                "parameters": [
                    {
                        "description": "user settings record to be added",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "apartment_number": {
                                    "type": "string"
                                },
                                "city": {
                                    "type": "string"
                                },
                                "company_name": {
                                    "type": "string"
                                },
                                "country": {
                                    "type": "string"
                                },
                                "customer": {
                                    "type": "string"
                                },
                                "customer_type": {
                                    "type": "string"
                                },
                                "email": {
                                    "type": "string"
                                },
                                "first_name": {
                                    "type": "string"
                                },
                                "last_name": {
                                    "type": "string"
                                },
                                "lat": {
                                    "type": "string"
                                },
                                "lng": {
                                    "type": "string"
                                },
                                "mobile_number": {
                                    "type": "string"
                                },
                                "network_operator": {
                                    "type": "string"
                                },
                                "phone_number": {
                                    "type": "string"
                                },
                                "postal_code": {
                                    "type": "string"
                                },
                                "province": {
                                    "type": "string"
                                },
                                "status": {
                                    "type": "string"
                                },
                                "street": {
                                    "type": "string"
                                },
                                "street_number": {
                                    "type": "string"
                                },
                                "url": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "postal_code"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "201": {
                        "description": "Sales Lead created"
                    },
                    "400": {
                        "description": "bad request or field values not valid"
                    },
                    "404": {
                        "description": "the provided customer does not exists"
                    },
                    "410": {
                        "description": "email address already used"
                    },
                    "411": {
                        "description": "address does not belong to a zone"
                    },
                    "413": {
                        "description": "zone status is not valid"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Create a new Sales Lead.",
                "tags": [
                    "coverage"
                ]
            },
            "put": {
                "description": "Update a Sales Lead.",
                "operationId": "putSalesLead",
                "parameters": [
                    {
                        "description": "updated user settings record",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "accept_survey_message": {
                                    "type": "string"
                                },
                                "apartment_number": {
                                    "type": "string"
                                },
                                "building": {
                                    "type": "string"
                                },
                                "bundle": {
                                    "type": "string"
                                },
                                "cancel_message": {
                                    "type": "string"
                                },
                                "city": {
                                    "type": "string"
                                },
                                "company_name": {
                                    "type": "string"
                                },
                                "country": {
                                    "type": "string"
                                },
                                "customer": {
                                    "type": "string"
                                },
                                "customer_type": {
                                    "type": "string"
                                },
                                "earlystart_message": {
                                    "type": "string"
                                },
                                "email": {
                                    "type": "string"
                                },
                                "first_name": {
                                    "type": "string"
                                },
                                "homedrop": {
                                    "type": "string"
                                },
                                "homedrop_index": {
                                    "type": "string"
                                },
                                "id": {
                                    "type": "string"
                                },
                                "last_name": {
                                    "type": "string"
                                },
                                "lat": {
                                    "type": "string"
                                },
                                "lng": {
                                    "type": "string"
                                },
                                "manual_check": {
                                    "type": "string"
                                },
                                "manual_check_price": {
                                    "type": "string"
                                },
                                "mobile_number": {
                                    "type": "string"
                                },
                                "multiple_homedrop": {
                                    "type": "string"
                                },
                                "object": {
                                    "type": "string"
                                },
                                "organization": {
                                    "type": "string"
                                },
                                "payment_tok": {
                                    "type": "string"
                                },
                                "phone_number": {
                                    "type": "string"
                                },
                                "province": {
                                    "type": "string"
                                },
                                "reject_survey_message": {
                                    "type": "string"
                                },
                                "service": {
                                    "type": "string"
                                },
                                "status": {
                                    "type": "string"
                                },
                                "street": {
                                    "type": "string"
                                },
                                "street_number": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "id"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "zone has been updated"
                    },
                    "403": {
                        "description": "permission"
                    },
                    "404": {
                        "description": "Sales Lead or other resource does not found"
                    },
                    "412": {
                        "description": "impossible to change status"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Update a Sales Lead.",
                "tags": [
                    "coverage"
                ]
            }
        },
        "/service": {
            "delete": {
                "description": "Delete a Service (if not used by any order).",
                "operationId": "deleteService",
                "parameters": [
                    {
                        "description": "Deleted a Service",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "id": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "id"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Service has been deleted",
                        "schema": {
                            "properties": {
                                "message": {
                                    "type": "string"
                                }
                            },
                            "type": "object"
                        }
                    },
                    "403": {
                        "$ref": "#/responses/403Forbidden"
                    },
                    "404": {
                        "$ref": "#/responses/404NotFound"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Delete a Service",
                "tags": [
                    "service"
                ]
            },
            "get": {
                "description": "Returns a list of service",
                "operationId": "getService",
                "parameters": [
                    {
                        "default": 1,
                        "description": "page requested",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 1000 entries is the maximum allowed value",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "collectionFormat": "csv",
                        "default": [
                            "id"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "by default all the fields are returned but if a subset is required, list all the ones that should be included in the response",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "fields",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "service list",
                        "schema": {
                            "properties": {
                                "data": {
                                    "items": {
                                        "$ref": "#/definitions/Service"
                                    },
                                    "type": "array"
                                }
                            },
                            "type": "object"
                        }
                    },
                    "404": {
                        "$ref": "#/responses/404NotFound"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get a list of services",
                "tags": [
                    "service"
                ]
            },
            "post": {
                "description": "Create an Service",
                "operationId": "postService",
                "parameters": [
                    {
                        "description": "Create a Service",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "auto_approve_move": {
                                    "type": "string"
                                },
                                "auto_approve_new": {
                                    "type": "string"
                                },
                                "bind_time": {
                                    "type": "string"
                                },
                                "definition": {
                                    "type": "string"
                                },
                                "description": {
                                    "type": "string"
                                },
                                "from_date": {
                                    "type": "string"
                                },
                                "name": {
                                    "type": "string"
                                },
                                "notice_time": {
                                    "type": "string"
                                },
                                "object_groups": {
                                    "type": "string"
                                },
                                "price": {
                                    "type": "string"
                                },
                                "referral_url": {
                                    "type": "string"
                                },
                                "service_provider": {
                                    "type": "string"
                                },
                                "service_type": {
                                    "type": "string"
                                },
                                "status": {
                                    "type": "string"
                                },
                                "to_date": {
                                    "type": "string"
                                },
                                "visibility": {
                                    "type": "string"
                                },
                                "vlans": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "object_groups",
                                "service_type",
                                "service_provider",
                                "description",
                                "name"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "201": {
                        "description": "service has been created",
                        "schema": {
                            "properties": {
                                "data": {
                                    "$ref": "#/definitions/Service"
                                },
                                "message": {
                                    "type": "string"
                                }
                            },
                            "type": "object"
                        }
                    },
                    "400": {
                        "$ref": "#/responses/400BadRequest"
                    },
                    "403": {
                        "$ref": "#/responses/403Forbidden"
                    },
                    "406": {
                        "$ref": "#/responses/406NotAcceptable"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Create an Service",
                "tags": [
                    "service"
                ]
            },
            "put": {
                "description": "Edit an Service",
                "operationId": "putService",
                "parameters": [
                    {
                        "description": "Edit a Service",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "auto_approve_move": {
                                    "type": "string"
                                },
                                "auto_approve_new": {
                                    "type": "string"
                                },
                                "bind_time": {
                                    "type": "string"
                                },
                                "definition": {
                                    "type": "string"
                                },
                                "description": {
                                    "type": "string"
                                },
                                "from_date": {
                                    "type": "string"
                                },
                                "name": {
                                    "type": "string"
                                },
                                "notice_time": {
                                    "type": "string"
                                },
                                "object_groups": {
                                    "type": "string"
                                },
                                "price": {
                                    "type": "string"
                                },
                                "referral_url": {
                                    "type": "string"
                                },
                                "service_provider": {
                                    "type": "string"
                                },
                                "service_type": {
                                    "type": "string"
                                },
                                "status": {
                                    "type": "string"
                                },
                                "to_date": {
                                    "type": "string"
                                },
                                "visibility": {
                                    "type": "string"
                                },
                                "vlans": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "object_groups",
                                "service_type",
                                "service_provider",
                                "description",
                                "name"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Service has been updated",
                        "schema": {
                            "properties": {
                                "data": {
                                    "$ref": "#/definitions/Service"
                                },
                                "message": {
                                    "type": "string"
                                }
                            },
                            "type": "object"
                        }
                    },
                    "400": {
                        "$ref": "#/responses/400BadRequest"
                    },
                    "404": {
                        "$ref": "#/responses/404NotFound"
                    },
                    "406": {
                        "$ref": "#/responses/406NotAcceptable"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Edit an Service",
                "tags": [
                    "service"
                ]
            }
        },
        "/service_category": {
            "get": {
                "description": "Returns a list of service categories",
                "operationId": "getServiceCategory",
                "parameters": [
                    {
                        "default": 1,
                        "description": "page requested",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 1000 entries is the maximum allowed value",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "collectionFormat": "csv",
                        "default": [
                            "id"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "by default all the fields are returned but if a subset is required, list all the ones that should be included in the response",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "fields",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "service category list",
                        "schema": {
                            "items": {
                                "properties": {
                                    "created": {
                                        "type": "string"
                                    },
                                    "id": {
                                        "type": "string"
                                    },
                                    "name": {
                                        "type": "string"
                                    },
                                    "parent": {
                                        "type": "string"
                                    },
                                    "updated": {
                                        "type": "string"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "404": {
                        "description": "service category was not found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get a list of service categories",
                "tags": [
                    "service_type"
                ]
            }
        },
        "/service_description": {
            "get": {
                "description": "Returns a list of service description",
                "operationId": "getServiceDescription",
                "parameters": [
                    {
                        "default": 1,
                        "description": "page requested",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 1000 entries is the maximum allowed value",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "collectionFormat": "csv",
                        "default": [
                            "id"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "by default all the fields are returned but if a subset is required, list all the ones that should be included in the response",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "fields",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "service description list",
                        "schema": {
                            "items": {
                                "properties": {
                                    "created": {
                                        "type": "string"
                                    },
                                    "description": {
                                        "type": "string"
                                    },
                                    "files": {
                                        "type": "string"
                                    },
                                    "id": {
                                        "type": "string"
                                    },
                                    "language": {
                                        "type": "string"
                                    },
                                    "name": {
                                        "type": "string"
                                    },
                                    "object_groups": {
                                        "type": "string"
                                    },
                                    "service": {
                                        "type": "string"
                                    },
                                    "service_provider": {
                                        "type": "string"
                                    },
                                    "short_description": {
                                        "type": "string"
                                    },
                                    "status": {
                                        "type": "string"
                                    },
                                    "updated": {
                                        "type": "string"
                                    },
                                    "welcome": {
                                        "type": "string"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "404": {
                        "description": "service description was not found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get a list of service description",
                "tags": [
                    "service"
                ]
            }
        },
        "/service_disruption": {
            "get": {
                "description": "Return a List of Service Disruption Events",
                "operationId": "getServiceDisruption",
                "parameters": [
                    {
                        "default": 1,
                        "description": "page requested",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 1000 entries is the maximum allowed value",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "collectionFormat": "csv",
                        "default": [
                            "id"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "by default all the fields are returned but if a subset is required, list all the ones that should be included in the response",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "fields",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Service Disruption event list",
                        "schema": {
                            "items": {
                                "properties": {
                                    "created": {
                                        "type": "string"
                                    },
                                    "down_objects": {
                                        "type": "string"
                                    },
                                    "duration": {
                                        "type": "string"
                                    },
                                    "id": {
                                        "type": "string"
                                    },
                                    "include": {
                                        "type": "string"
                                    },
                                    "network": {
                                        "type": "string"
                                    },
                                    "network_operator": {
                                        "type": "string"
                                    },
                                    "note": {
                                        "type": "string"
                                    },
                                    "start": {
                                        "type": "string"
                                    },
                                    "stop": {
                                        "type": "string"
                                    },
                                    "switch": {
                                        "type": "string"
                                    },
                                    "switch_name": {
                                        "type": "string"
                                    },
                                    "updated": {
                                        "type": "string"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "403": {
                        "description": "Not authorized to access"
                    },
                    "404": {
                        "description": "No Service Disruption events found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get Service Disruption events",
                "tags": [
                    "network"
                ]
            },
            "put": {
                "description": "Update a Service Disruption event.",
                "operationId": "putServiceDisruption",
                "parameters": [
                    {
                        "description": "IP Address to be updated",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "id": {
                                    "type": "string"
                                },
                                "include": {
                                    "type": "string"
                                },
                                "note": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "id"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Service Disruption event updated"
                    },
                    "400": {
                        "description": "Bad request or field values not valid"
                    },
                    "404": {
                        "description": "one or more of the provided field does not exists"
                    },
                    "406": {
                        "description": "backend error"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Update a Service Disruption event.",
                "tags": [
                    "network"
                ]
            }
        },
        "/service_price": {
            "get": {
                "description": "Returns a list of service prices",
                "operationId": "getServicePrice",
                "parameters": [
                    {
                        "default": 1,
                        "description": "page requested",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 1000 entries is the maximum allowed value",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "collectionFormat": "csv",
                        "default": [
                            "id"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "by default all the fields are returned but if a subset is required, list all the ones that should be included in the response",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "fields",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "service price list",
                        "schema": {
                            "items": {
                                "properties": {
                                    "created": {
                                        "type": "string"
                                    },
                                    "id": {
                                        "type": "string"
                                    },
                                    "object_group": {
                                        "type": "string"
                                    },
                                    "price": {
                                        "type": "string"
                                    },
                                    "service": {
                                        "type": "string"
                                    },
                                    "service_provider": {
                                        "type": "string"
                                    },
                                    "status": {
                                        "type": "string"
                                    },
                                    "type": {
                                        "type": "string"
                                    },
                                    "updated": {
                                        "type": "string"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "404": {
                        "description": "service prices was not found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get a list of service prices",
                "tags": [
                    "service"
                ]
            }
        },
        "/service_prices_fees": {
            "get": {
                "description": "Returns a list of service proces and fees split for object_group queried by service_type and service_provider<br/>The info is already available in the service. This resource is necessary when creating a new service",
                "operationId": "getServicePricesFees",
                "parameters": [
                    {
                        "description": "service provider",
                        "in": "query",
                        "name": "service_provider",
                        "type": "string"
                    },
                    {
                        "description": "service type",
                        "in": "query",
                        "name": "service_type",
                        "type": "string"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "daily statistics",
                        "schema": {
                            "items": {
                                "properties": {
                                    "annual_fee_price": {
                                        "type": "number"
                                    },
                                    "change_fee": {
                                        "type": "number"
                                    },
                                    "monthly_fee": {
                                        "type": "number"
                                    },
                                    "monthly_price": {
                                        "type": "number"
                                    },
                                    "move_fee": {
                                        "type": "number"
                                    },
                                    "object_group": {
                                        "type": "string"
                                    },
                                    "object_group_name": {
                                        "type": "string"
                                    },
                                    "start_fee": {
                                        "type": "number"
                                    },
                                    "start_price": {
                                        "type": "number"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "404": {
                        "description": "item not found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get a list of service prices and fees split for object_group queried by service_type and service_provider",
                "tags": [
                    "service"
                ]
            }
        },
        "/service_provider": {
            "get": {
                "description": "Returns a list of service providers",
                "operationId": "getServiceProvider",
                "parameters": [
                    {
                        "default": 1,
                        "description": "page requested",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 1000 entries is the maximum allowed value",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "collectionFormat": "csv",
                        "default": [
                            "id"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "by default all the fields are returned but if a subset is required, list all the ones that should be included in the response",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "fields",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "service provider list",
                        "schema": {
                            "items": {
                                "properties": {
                                    "address": {
                                        "type": "string"
                                    },
                                    "city": {
                                        "type": "string"
                                    },
                                    "created": {
                                        "type": "string"
                                    },
                                    "customer_phone": {
                                        "type": "string"
                                    },
                                    "email": {
                                        "type": "string"
                                    },
                                    "full_name": {
                                        "type": "string"
                                    },
                                    "id": {
                                        "type": "string"
                                    },
                                    "name": {
                                        "type": "string"
                                    },
                                    "object_groups": {
                                        "type": "string"
                                    },
                                    "postal_code": {
                                        "type": "string"
                                    },
                                    "service_types": {
                                        "type": "string"
                                    },
                                    "status": {
                                        "enum": [
                                            [
                                                "u'Public'",
                                                "u'Not Public'"
                                            ]
                                        ],
                                        "type": "string"
                                    },
                                    "support_saturday": {
                                        "type": "string"
                                    },
                                    "support_sunday": {
                                        "type": "string"
                                    },
                                    "support_weekdays": {
                                        "type": "string"
                                    },
                                    "updated": {
                                        "type": "string"
                                    },
                                    "url": {
                                        "type": "string"
                                    },
                                    "vlan": {
                                        "type": "string"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "404": {
                        "description": "no service provider records found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get a list of service providers",
                "tags": [
                    "service provider"
                ]
            }
        },
        "/service_speed": {
            "delete": {
                "description": "Delete a Service Speed (If not used by any Service Type).",
                "operationId": "deleteServiceSpeed",
                "parameters": [
                    {
                        "description": "Delete a Service Speed",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "id": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "id"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Service Speed has been deleted"
                    },
                    "403": {
                        "description": "Permission issue"
                    },
                    "404": {
                        "description": "Service Speed not found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Delete a Service Speed",
                "tags": [
                    "service_type"
                ]
            },
            "get": {
                "description": "Returns a list of service speed in Mbps",
                "operationId": "getServiceSpeed",
                "parameters": [
                    {
                        "default": 1,
                        "description": "page requested",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 1000 entries is the maximum allowed value",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "collectionFormat": "csv",
                        "default": [
                            "id"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "by default all the fields are returned but if a subset is required, list all the ones that should be included in the response",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "fields",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Service Speed list",
                        "schema": {
                            "items": {
                                "properties": {
                                    "created": {
                                        "type": "string"
                                    },
                                    "download_speed": {
                                        "type": "string"
                                    },
                                    "id": {
                                        "type": "string"
                                    },
                                    "speed_id": {
                                        "type": "string"
                                    },
                                    "updated": {
                                        "type": "string"
                                    },
                                    "upload_speed": {
                                        "type": "string"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "404": {
                        "description": "Service Speed not found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get a list of service speed",
                "tags": [
                    "service_type"
                ]
            },
            "post": {
                "description": "Create a Service Speed",
                "operationId": "postServiceSpeed",
                "parameters": [
                    {
                        "description": "Create a Service Speed",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "download_speed": {
                                    "type": "string"
                                },
                                "speed_id": {
                                    "type": "string"
                                },
                                "upload_speed": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "upload_speed",
                                "speed_id",
                                "download_speed"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "201": {
                        "description": "Service Speed has been added"
                    },
                    "406": {
                        "description": "Error from backend server"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Create a Service Speed",
                "tags": [
                    "service_type"
                ]
            },
            "put": {
                "description": "Edit a Service Speed",
                "operationId": "putServiceSpeed",
                "parameters": [
                    {
                        "description": "Update a Service Speed",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "download_speed": {
                                    "type": "string"
                                },
                                "id": {
                                    "type": "string"
                                },
                                "speed_id": {
                                    "type": "string"
                                },
                                "upload_speed": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "id"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Service Speed has been updated"
                    },
                    "400": {
                        "description": "Generic Error"
                    },
                    "404": {
                        "description": "Service Speed not found"
                    },
                    "406": {
                        "description": "Error from backend server"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Edit a Service Speed",
                "tags": [
                    "service_type"
                ]
            }
        },
        "/service_type": {
            "get": {
                "description": "Returns a list of service type",
                "operationId": "getServiceType",
                "parameters": [
                    {
                        "default": 1,
                        "description": "page requested",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 1000 entries is the maximum allowed value",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "collectionFormat": "csv",
                        "default": [
                            "id"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "by default all the fields are returned but if a subset is required, list all the ones that should be included in the response",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "fields",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "service type list",
                        "schema": {
                            "items": {
                                "properties": {
                                    "allow_activation_date_editing": {
                                        "type": "string"
                                    },
                                    "allow_inactivation_date_editing": {
                                        "type": "string"
                                    },
                                    "allow_move": {
                                        "type": "string"
                                    },
                                    "allow_provisioning_changes": {
                                        "type": "string"
                                    },
                                    "assign_ip_addresses": {
                                        "type": "string"
                                    },
                                    "cpe_required": {
                                        "type": "string"
                                    },
                                    "created": {
                                        "type": "string"
                                    },
                                    "customer_move_allowed": {
                                        "type": "string"
                                    },
                                    "customer_type": {
                                        "type": "string"
                                    },
                                    "definition": {
                                        "type": "string"
                                    },
                                    "fee_group": {
                                        "type": "string"
                                    },
                                    "from_date": {
                                        "type": "string"
                                    },
                                    "id": {
                                        "type": "string"
                                    },
                                    "manual_activation": {
                                        "type": "string"
                                    },
                                    "manual_termination": {
                                        "type": "string"
                                    },
                                    "name": {
                                        "type": "string"
                                    },
                                    "object_groups": {
                                        "type": "string"
                                    },
                                    "parking_allowed": {
                                        "type": "string"
                                    },
                                    "port_control_provisioned": {
                                        "type": "string"
                                    },
                                    "require_active_object": {
                                        "type": "string"
                                    },
                                    "require_switch_connection": {
                                        "type": "string"
                                    },
                                    "service_category": {
                                        "type": "string"
                                    },
                                    "service_providers": {
                                        "type": "string"
                                    },
                                    "service_speed": {
                                        "type": "string"
                                    },
                                    "status": {
                                        "type": "string"
                                    },
                                    "to_date": {
                                        "type": "string"
                                    },
                                    "updated": {
                                        "type": "string"
                                    },
                                    "visibility": {
                                        "type": "string"
                                    },
                                    "vlan_type": {
                                        "type": "string"
                                    },
                                    "wait_for_cpe_acknowledgement": {
                                        "type": "string"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "404": {
                        "description": "service type was not found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get a list of service type",
                "tags": [
                    "service_type"
                ]
            }
        },
        "/service_type_fee": {
            "get": {
                "description": "Returns a list of service type fee",
                "operationId": "getServiceTypeFee",
                "parameters": [
                    {
                        "default": 1,
                        "description": "page requested",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 1000 entries is the maximum allowed value",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "collectionFormat": "csv",
                        "default": [
                            "id"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "by default all the fields are returned but if a subset is required, list all the ones that should be included in the response",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "fields",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "service price list",
                        "schema": {
                            "items": {
                                "properties": {
                                    "created": {
                                        "type": "string"
                                    },
                                    "fee_group": {
                                        "type": "string"
                                    },
                                    "id": {
                                        "type": "string"
                                    },
                                    "name": {
                                        "type": "string"
                                    },
                                    "object_group": {
                                        "type": "string"
                                    },
                                    "price": {
                                        "type": "string"
                                    },
                                    "service_provider": {
                                        "type": "string"
                                    },
                                    "type": {
                                        "type": "string"
                                    },
                                    "updated": {
                                        "type": "string"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "404": {
                        "description": "service prices was not found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get a list of service type fee",
                "tags": [
                    "service_type"
                ]
            }
        },
        "/site": {
            "delete": {
                "description": "Delete a Site (if it has no switches).",
                "operationId": "deleteSite",
                "parameters": [
                    {
                        "description": "Delete a Site",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "id": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "id"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Site has been deleted"
                    },
                    "403": {
                        "description": "Permission issue"
                    },
                    "404": {
                        "description": "Site not found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Delete a Site",
                "tags": [
                    "network"
                ]
            },
            "get": {
                "description": "Returns a list of network switch Sites",
                "operationId": "getSite",
                "parameters": [
                    {
                        "default": 1,
                        "description": "page requested",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 1000 entries is the maximum allowed value",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "collectionFormat": "csv",
                        "default": [
                            "id"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "by default all the fields are returned but if a subset is required, list all the ones that should be included in the response",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "fields",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "network switch Site list",
                        "schema": {
                            "items": {
                                "properties": {
                                    "created": {
                                        "type": "string"
                                    },
                                    "description": {
                                        "type": "string"
                                    },
                                    "id": {
                                        "type": "string"
                                    },
                                    "latitude": {
                                        "type": "string"
                                    },
                                    "longitude": {
                                        "type": "string"
                                    },
                                    "name": {
                                        "type": "string"
                                    },
                                    "note": {
                                        "type": "string"
                                    },
                                    "postal_code": {
                                        "type": "string"
                                    },
                                    "street": {
                                        "type": "string"
                                    },
                                    "street_number": {
                                        "type": "string"
                                    },
                                    "updated": {
                                        "type": "string"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "403": {
                        "description": "not authorized to access"
                    },
                    "404": {
                        "description": "no Sites found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get a list of network switch Sites",
                "tags": [
                    "network"
                ]
            },
            "post": {
                "description": "Create a Site",
                "operationId": "postSite",
                "parameters": [
                    {
                        "description": "Create a Site",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "description": {
                                    "type": "string"
                                },
                                "name": {
                                    "type": "string"
                                },
                                "note": {
                                    "type": "string"
                                },
                                "postal_code": {
                                    "type": "string"
                                },
                                "street": {
                                    "type": "string"
                                },
                                "street_number": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "description",
                                "name"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "201": {
                        "description": "Site has been added"
                    },
                    "406": {
                        "description": "Error from backend server"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Create a Site",
                "tags": [
                    "network"
                ]
            },
            "put": {
                "description": "Edit a Site",
                "operationId": "putSite",
                "parameters": [
                    {
                        "description": "Update Site",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "description": {
                                    "type": "string"
                                },
                                "id": {
                                    "type": "string"
                                },
                                "name": {
                                    "type": "string"
                                },
                                "note": {
                                    "type": "string"
                                },
                                "postal_code": {
                                    "type": "string"
                                },
                                "street": {
                                    "type": "string"
                                },
                                "street_number": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "id"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Site has been updated"
                    },
                    "400": {
                        "description": "Generic Error"
                    },
                    "404": {
                        "description": "Site was not found"
                    },
                    "406": {
                        "description": "Error from backend server"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Edit a Site",
                "tags": [
                    "network"
                ]
            }
        },
        "/stripe/events": {
            "post": {
                "description": "",
                "operationId": "postStripeEvents",
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "201": {
                        "description": "event management has been completed"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Webhook for events's stripe",
                "tags": [
                    "workflow"
                ]
            }
        },
        "/switch": {
            "get": {
                "description": "Returns a list of network switch",
                "parameters": [
                    {
                        "default": 1,
                        "description": "page requested",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 1000 entries is the maximum allowed value",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "collectionFormat": "csv",
                        "default": [
                            "id"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "by default all the fields are returned but if a subset is required, list all the ones that should be included in the response",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "fields",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "network operator list",
                        "schema": {
                            "properties": {
                                "data": {
                                    "items": {
                                        "properties": {
                                            "active_ports": {
                                                "type": "string"
                                            },
                                            "address": {
                                                "type": "string"
                                            },
                                            "created": {
                                                "type": "string"
                                            },
                                            "down_since": {
                                                "type": "string"
                                            },
                                            "down_users": {
                                                "type": "string"
                                            },
                                            "driver": {
                                                "type": "string"
                                            },
                                            "id": {
                                                "type": "string"
                                            },
                                            "model": {
                                                "type": "string"
                                            },
                                            "name": {
                                                "type": "string"
                                            },
                                            "network": {
                                                "type": "string"
                                            },
                                            "network_operator": {
                                                "type": "string"
                                            },
                                            "number_of_ports": {
                                                "type": "string"
                                            },
                                            "parent1": {
                                                "type": "string"
                                            },
                                            "parent2": {
                                                "type": "string"
                                            },
                                            "peripheral": {
                                                "type": "string"
                                            },
                                            "site": {
                                                "type": "string"
                                            },
                                            "status": {
                                                "enum": [
                                                    [
                                                        "u'Active'",
                                                        "u'Inactive'"
                                                    ]
                                                ],
                                                "type": "string"
                                            },
                                            "updated": {
                                                "type": "string"
                                            }
                                        },
                                        "type": "object"
                                    },
                                    "type": "array"
                                }
                            },
                            "type": "object"
                        }
                    },
                    "403": {
                        "description": "not authorized to access"
                    },
                    "404": {
                        "description": "no network operators records found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get a list of network switch",
                "tags": [
                    "network"
                ]
            }
        },
        "/switch/info": {
            "get": {
                "description": "Get information about the switch",
                "operationId": "getSwitchInfo",
                "parameters": [
                    {
                        "description": "switch id or switch name",
                        "in": "query",
                        "name": "switch",
                        "type": "string"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Switch information",
                        "schema": {
                            "properties": {
                                "data": {
                                    "properties": {
                                        "switch": {
                                            "type": "string"
                                        },
                                        "system": {
                                            "type": "object"
                                        },
                                        "timestamp": {
                                            "type": "string"
                                        }
                                    },
                                    "type": "object"
                                }
                            },
                            "type": "object"
                        }
                    },
                    "400": {
                        "description": "Bad requests"
                    },
                    "404": {
                        "description": "Switch unknown"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get information about the switch",
                "tags": [
                    "network"
                ]
            }
        },
        "/workflow/message": {
            "post": {
                "description": "",
                "operationId": "postWorkflowMessage",
                "parameters": [
                    {
                        "description": "Send a message to the workflow",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "business_key": {
                                    "type": "string"
                                },
                                "name": {
                                    "type": "string"
                                },
                                "process_definition_key": {
                                    "type": "string"
                                },
                                "variables": {
                                    "type": "object"
                                }
                            },
                            "required": [
                                "name",
                                "process_definition_key",
                                "business_key"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "201": {
                        "description": "Workflow message has been sent"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Send a message to workflow",
                "tags": [
                    "workflow"
                ]
            }
        },
        "/workflow/task": {
            "get": {
                "description": "Get the pending workflow human task",
                "operationId": "getWorkflowTask",
                "parameters": [
                    {
                        "description": "process business key",
                        "in": "query",
                        "name": "process_instance_business_key",
                        "required": True,
                        "type": "string"
                    },
                    {
                        "description": "definition_key",
                        "in": "query",
                        "name": "process_definition_key",
                        "required": True,
                        "type": "string"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "current human task"
                    },
                    "403": {
                        "description": "not authorized to access"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get the pending workflow human task",
                "tags": [
                    "workflow"
                ]
            },
            "post": {
                "description": "",
                "operationId": "postWorkflowTask",
                "parameters": [
                    {
                        "description": "Complete a workflow task",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "business_key": {
                                    "type": "string"
                                },
                                "process_definition_key": {
                                    "type": "string"
                                },
                                "variables": {
                                    "type": "object"
                                }
                            },
                            "required": [
                                "process_definition_key",
                                "business_key"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "201": {
                        "description": "Workflow task has been completed"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Complete workflow task",
                "tags": [
                    "workflow"
                ]
            }
        },
        "/zone": {
            "delete": {
                "description": "Delete a Zone. id must be provided.",
                "parameters": [
                    {
                        "description": "deleted user settings record",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "id": {
                                    "type": "string"
                                },
                                "network_operator": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "id",
                                "network_operator"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "Zone has been deleted"
                    },
                    "403": {
                        "description": "Permission issue"
                    },
                    "404": {
                        "description": "Zone not found"
                    },
                    "410": {
                        "description": "Zone is already used"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Delete a Zone.",
                "tags": [
                    "coverage"
                ]
            },
            "get": {
                "description": "Returns a list of zone. A zone belongs to a network_operator. The zone name is unique.<br/>The area field is a GeoJSON MultiPolygon (www.geojson.org).",
                "operationId": "getZone",
                "parameters": [
                    {
                        "default": 1,
                        "description": "page requested",
                        "in": "query",
                        "name": "page",
                        "type": "integer"
                    },
                    {
                        "default": 30,
                        "description": "the maximum number of entries returned in a page, 1000 entries is the maximum allowed value",
                        "in": "query",
                        "name": "per_page",
                        "type": "integer"
                    },
                    {
                        "collectionFormat": "csv",
                        "default": [
                            "id"
                        ],
                        "description": "fields we want items to be order by; default is ascending, prefix field name with - for discending ordering",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "sort",
                        "type": "array"
                    },
                    {
                        "description": "search for entries with specific fields values, list them as field:value",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "q",
                        "type": "array"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "by default all the fields are returned but if a subset is required, list all the ones that should be included in the response",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "fields",
                        "type": "array"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "zone record list",
                        "schema": {
                            "items": {
                                "properties": {
                                    "allow_service_order": {
                                        "type": "string"
                                    },
                                    "area": {
                                        "type": "string"
                                    },
                                    "created": {
                                        "type": "string"
                                    },
                                    "home_drop": {
                                        "type": "string"
                                    },
                                    "id": {
                                        "type": "string"
                                    },
                                    "name": {
                                        "type": "string"
                                    },
                                    "network_operator": {
                                        "type": "string"
                                    },
                                    "object_group": {
                                        "type": "string"
                                    },
                                    "status": {
                                        "type": "string"
                                    },
                                    "updated": {
                                        "type": "string"
                                    }
                                },
                                "type": "object"
                            },
                            "type": "array"
                        }
                    },
                    "404": {
                        "description": "no zone records found"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Get zones",
                "tags": [
                    "coverage"
                ]
            },
            "post": {
                "description": "Create a new zone. A zone belongs to a network_operator. The zone name must be unique.<br/>The area field is a GeoJSON MultiPolygon (www.geojson.org). network_operator field is always mandatory.",
                "operationId": "postZone",
                "parameters": [
                    {
                        "description": "user settings record to be added",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "allow_service_order": {
                                    "type": "string"
                                },
                                "area": {
                                    "type": "string"
                                },
                                "home_drop": {
                                    "type": "string"
                                },
                                "name": {
                                    "type": "string"
                                },
                                "network_operator": {
                                    "type": "string"
                                },
                                "object_group": {
                                    "type": "string"
                                },
                                "status": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "status",
                                "name",
                                "network_operator",
                                "area"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "201": {
                        "description": "created settings"
                    },
                    "410": {
                        "description": "area field error"
                    },
                    "411": {
                        "description": "network_operator is unknown"
                    },
                    "412": {
                        "description": "zone with the same username already exists"
                    },
                    "413": {
                        "description": "zone status is not valid"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Create a new zone.",
                "tags": [
                    "coverage"
                ]
            },
            "put": {
                "description": "Update zone. A zone belongs to a network_operator. The zone name is unique.<br/>The area field is a GeoJSON MultiPolygon (www.geojson.org). network_operator field is always mandatory.",
                "operationId": "putZone",
                "parameters": [
                    {
                        "description": "updated user settings record",
                        "in": "body",
                        "name": "body",
                        "schema": {
                            "properties": {
                                "allow_service_order": {
                                    "type": "string"
                                },
                                "area": {
                                    "type": "string"
                                },
                                "home_drop": {
                                    "type": "string"
                                },
                                "id": {
                                    "type": "string"
                                },
                                "name": {
                                    "type": "string"
                                },
                                "network_operator": {
                                    "type": "string"
                                },
                                "object_group": {
                                    "type": "string"
                                },
                                "status": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "network_operator",
                                "id"
                            ],
                            "type": "object"
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "zone has been updated"
                    },
                    "404": {
                        "description": "zone not found"
                    },
                    "410": {
                        "description": "area field error"
                    },
                    "412": {
                        "description": "zone name already exists"
                    },
                    "413": {
                        "description": "status not valid"
                    }
                },
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "summary": "Update a zone.",
                "tags": [
                    "coverage"
                ]
            }
        }
    },
    "responses": {
        "400BadRequest": {
            "description": "resource was not found",
            "schema": {
                "$ref": "#/definitions/HTTPError4XX"
            }
        },
        "401Unauthorized": {
            "description": "not authorized",
            "schema": {
                "$ref": "#/definitions/HTTPError4XX"
            }
        },
        "403Forbidden": {
            "description": "not allowed access to this resource",
            "schema": {
                "$ref": "#/definitions/HTTPError4XX"
            }
        },
        "404NotFound": {
            "description": "The specified resource was not found",
            "schema": {
                "$ref": "#/definitions/HTTPError4XX"
            }
        },
        "405MethodNotAllowed": {
            "description": "the method is not allowed",
            "schema": {
                "$ref": "#/definitions/HTTPError4XX"
            }
        },
        "406NotAcceptable": {
            "description": "the request was not acceptead by the api",
            "schema": {
                "$ref": "#/definitions/HTTPError4XX"
            }
        },
        "408RequestTimeout": {
            "description": "timeout trying to reach the resource",
            "schema": {
                "$ref": "#/definitions/HTTPError4XX"
            }
        },
        "409Conflict": {
            "description": "conflict, resource already exists",
            "schema": {
                "$ref": "#/definitions/HTTPError4XX"
            }
        },
        "410Gone": {
            "description": "the specified resource has dissapered",
            "schema": {
                "$ref": "#/definitions/HTTPError4XX"
            }
        },
        "412PreconditionFailed": {
            "description": "resource already exists or other pre-condition error",
            "schema": {
                "$ref": "#/definitions/HTTPError4XX"
            }
        },
        "413PayloadTooLarge": {
            "description": "the payoad is to large, https://tools.ietf.org/html/rfc7231)",
            "schema": {
                "$ref": "#/definitions/HTTPError4XX"
            }
        }
    },
    "securityDefinitions": {
        "api_key": {
            "in": "header",
            "name": "api_key",
            "type": "apiKey"
        },
        "basicAuth": {
            "type": "basic"
        }
    },
    "swagger": "2.0"
}
