/* tslint:disable */
/* eslint-disable */
/**
 * Easylog No description provided (generated by Openapi Generator
 * https://github.com/openapitools/openapi-generator)
 *
 * The version of the OpenAPI document: 0.2.0
 *
 * NOTE: This class is auto generated by OpenAPI Generator
 * (https://openapi-generator.tech). https://openapi-generator.tech Do not edit
 * the class manually.
 */

import { mapValues } from '../runtime';
import type { V2ChatChatIdMessagesGet200Response } from './V2ChatChatIdMessagesGet200Response';
import {
  V2ChatChatIdMessagesGet200ResponseFromJSON,
  V2ChatChatIdMessagesGet200ResponseFromJSONTyped,
  V2ChatChatIdMessagesGet200ResponseToJSON,
  V2ChatChatIdMessagesGet200ResponseToJSONTyped
} from './V2ChatChatIdMessagesGet200Response';

/**
 * @export
 * @interface ChatResource
 */
export interface ChatResource {
  /**
   * @memberof ChatResource
   * @type {number}
   */
  id?: number;
  /**
   * @memberof ChatResource
   * @type {number}
   */
  clientId?: number;
  /**
   * @memberof ChatResource
   * @type {string}
   */
  chattableType?: string;
  /**
   * @memberof ChatResource
   * @type {number}
   */
  chattableId?: number;
  /**
   * @memberof ChatResource
   * @type {string}
   */
  name?: string;
  /**
   * @memberof ChatResource
   * @type {V2ChatChatIdMessagesGet200Response}
   */
  messages?: V2ChatChatIdMessagesGet200Response;
  /**
   * @memberof ChatResource
   * @type {Date}
   */
  createdAt?: Date;
  /**
   * @memberof ChatResource
   * @type {Date}
   */
  updatedAt?: Date;
}

/** Check if a given object implements the ChatResource interface. */
export function instanceOfChatResource(value: object): value is ChatResource {
  return true;
}

export function ChatResourceFromJSON(json: any): ChatResource {
  return ChatResourceFromJSONTyped(json, false);
}

export function ChatResourceFromJSONTyped(
  json: any,
  ignoreDiscriminator: boolean
): ChatResource {
  if (json == null) {
    return json;
  }
  return {
    id: json['id'] == null ? undefined : json['id'],
    clientId: json['client_id'] == null ? undefined : json['client_id'],
    chattableType:
      json['chattable_type'] == null ? undefined : json['chattable_type'],
    chattableId:
      json['chattable_id'] == null ? undefined : json['chattable_id'],
    name: json['name'] == null ? undefined : json['name'],
    messages:
      json['messages'] == null
        ? undefined
        : V2ChatChatIdMessagesGet200ResponseFromJSON(json['messages']),
    createdAt:
      json['created_at'] == null ? undefined : new Date(json['created_at']),
    updatedAt:
      json['updated_at'] == null ? undefined : new Date(json['updated_at'])
  };
}

export function ChatResourceToJSON(json: any): ChatResource {
  return ChatResourceToJSONTyped(json, false);
}

export function ChatResourceToJSONTyped(
  value?: ChatResource | null,
  ignoreDiscriminator: boolean = false
): any {
  if (value == null) {
    return value;
  }

  return {
    id: value['id'],
    client_id: value['clientId'],
    chattable_type: value['chattableType'],
    chattable_id: value['chattableId'],
    name: value['name'],
    messages: V2ChatChatIdMessagesGet200ResponseToJSON(value['messages']),
    created_at:
      value['createdAt'] == null ? undefined : value['createdAt'].toISOString(),
    updated_at:
      value['updatedAt'] == null ? undefined : value['updatedAt'].toISOString()
  };
}
