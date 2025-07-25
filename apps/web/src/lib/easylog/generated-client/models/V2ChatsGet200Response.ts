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
import type { ChatResource } from './ChatResource';
import {
  ChatResourceFromJSON,
  ChatResourceFromJSONTyped,
  ChatResourceToJSON,
  ChatResourceToJSONTyped
} from './ChatResource';

/**
 * @export
 * @interface V2ChatsGet200Response
 */
export interface V2ChatsGet200Response {
  /**
   * @memberof V2ChatsGet200Response
   * @type {ChatResource[]}
   */
  data?: Array<ChatResource>;
}

/** Check if a given object implements the V2ChatsGet200Response interface. */
export function instanceOfV2ChatsGet200Response(
  value: object
): value is V2ChatsGet200Response {
  return true;
}

export function V2ChatsGet200ResponseFromJSON(
  json: any
): V2ChatsGet200Response {
  return V2ChatsGet200ResponseFromJSONTyped(json, false);
}

export function V2ChatsGet200ResponseFromJSONTyped(
  json: any,
  ignoreDiscriminator: boolean
): V2ChatsGet200Response {
  if (json == null) {
    return json;
  }
  return {
    data:
      json['data'] == null
        ? undefined
        : (json['data'] as Array<any>).map(ChatResourceFromJSON)
  };
}

export function V2ChatsGet200ResponseToJSON(json: any): V2ChatsGet200Response {
  return V2ChatsGet200ResponseToJSONTyped(json, false);
}

export function V2ChatsGet200ResponseToJSONTyped(
  value?: V2ChatsGet200Response | null,
  ignoreDiscriminator: boolean = false
): any {
  if (value == null) {
    return value;
  }

  return {
    data:
      value['data'] == null
        ? undefined
        : (value['data'] as Array<any>).map(ChatResourceToJSON)
  };
}
