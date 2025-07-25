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
import type { ChatMessageResource } from './ChatMessageResource';
import {
  ChatMessageResourceFromJSON,
  ChatMessageResourceFromJSONTyped,
  ChatMessageResourceToJSON,
  ChatMessageResourceToJSONTyped
} from './ChatMessageResource';

/**
 * @export
 * @interface V2ChatChatIdMessagesGet200Response
 */
export interface V2ChatChatIdMessagesGet200Response {
  /**
   * @memberof V2ChatChatIdMessagesGet200Response
   * @type {ChatMessageResource[]}
   */
  data?: Array<ChatMessageResource>;
}

/**
 * Check if a given object implements the V2ChatChatIdMessagesGet200Response
 * interface.
 */
export function instanceOfV2ChatChatIdMessagesGet200Response(
  value: object
): value is V2ChatChatIdMessagesGet200Response {
  return true;
}

export function V2ChatChatIdMessagesGet200ResponseFromJSON(
  json: any
): V2ChatChatIdMessagesGet200Response {
  return V2ChatChatIdMessagesGet200ResponseFromJSONTyped(json, false);
}

export function V2ChatChatIdMessagesGet200ResponseFromJSONTyped(
  json: any,
  ignoreDiscriminator: boolean
): V2ChatChatIdMessagesGet200Response {
  if (json == null) {
    return json;
  }
  return {
    data:
      json['data'] == null
        ? undefined
        : (json['data'] as Array<any>).map(ChatMessageResourceFromJSON)
  };
}

export function V2ChatChatIdMessagesGet200ResponseToJSON(
  json: any
): V2ChatChatIdMessagesGet200Response {
  return V2ChatChatIdMessagesGet200ResponseToJSONTyped(json, false);
}

export function V2ChatChatIdMessagesGet200ResponseToJSONTyped(
  value?: V2ChatChatIdMessagesGet200Response | null,
  ignoreDiscriminator: boolean = false
): any {
  if (value == null) {
    return value;
  }

  return {
    data:
      value['data'] == null
        ? undefined
        : (value['data'] as Array<any>).map(ChatMessageResourceToJSON)
  };
}
