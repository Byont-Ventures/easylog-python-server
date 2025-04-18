/* tslint:disable */
/* eslint-disable */
/**
 * FastAPI No description provided (generated by Openapi Generator
 * https://github.com/openapitools/openapi-generator)
 *
 * The version of the OpenAPI document: 0.1.0
 *
 * NOTE: This class is auto generated by OpenAPI Generator
 * (https://openapi-generator.tech). https://openapi-generator.tech Do not edit
 * the class manually.
 */

import { mapValues } from '../runtime';
import type { MessageContentType } from './MessageContentType';
import {
  MessageContentTypeFromJSON,
  MessageContentTypeFromJSONTyped,
  MessageContentTypeToJSON,
  MessageContentTypeToJSONTyped
} from './MessageContentType';
import type { Messages } from './Messages';
import {
  MessagesFromJSON,
  MessagesFromJSONTyped,
  MessagesToJSON,
  MessagesToJSONTyped
} from './Messages';
import type { MessageContentFormat } from './MessageContentFormat';
import {
  MessageContentFormatFromJSON,
  MessageContentFormatFromJSONTyped,
  MessageContentFormatToJSON,
  MessageContentFormatToJSONTyped
} from './MessageContentFormat';

/**
 * Represents a message_contents record
 *
 * @export
 * @interface MessageContents
 */
export interface MessageContents {
  /**
   * @memberof MessageContents
   * @type {string}
   */
  id: string;
  /**
   * @memberof MessageContents
   * @type {Messages}
   */
  message?: Messages | null;
  /**
   * @memberof MessageContents
   * @type {string}
   */
  message_id: string;
  /**
   * @memberof MessageContents
   * @type {MessageContentType}
   */
  type: MessageContentType;
  /**
   * @memberof MessageContents
   * @type {string}
   */
  tool_use_id?: string | null;
  /**
   * @memberof MessageContents
   * @type {boolean}
   */
  tool_use_is_error?: boolean | null;
  /**
   * @memberof MessageContents
   * @type {string}
   */
  tool_use_name?: string | null;
  /**
   * @memberof MessageContents
   * @type
   */
  tool_use_input?: null;
  /**
   * @memberof MessageContents
   * @type {string}
   */
  content?: string | null;
  /**
   * @memberof MessageContents
   * @type {string}
   */
  content_type?: string | null;
  /**
   * @memberof MessageContents
   * @type {MessageContentFormat}
   */
  content_format: MessageContentFormat;
  /**
   * @memberof MessageContents
   * @type {string}
   */
  data?: string | null;
  /**
   * @memberof MessageContents
   * @type {Date}
   */
  created_at: Date;
  /**
   * @memberof MessageContents
   * @type {Date}
   */
  updated_at: Date;
}

/** Check if a given object implements the MessageContents interface. */
export function instanceOfMessageContents(
  value: object
): value is MessageContents {
  if (!('id' in value) || value['id'] === undefined) return false;
  if (!('message_id' in value) || value['message_id'] === undefined)
    return false;
  if (!('type' in value) || value['type'] === undefined) return false;
  if (!('content_format' in value) || value['content_format'] === undefined)
    return false;
  if (!('created_at' in value) || value['created_at'] === undefined)
    return false;
  if (!('updated_at' in value) || value['updated_at'] === undefined)
    return false;
  return true;
}

export function MessageContentsFromJSON(json: any): MessageContents {
  return MessageContentsFromJSONTyped(json, false);
}

export function MessageContentsFromJSONTyped(
  json: any,
  ignoreDiscriminator: boolean
): MessageContents {
  if (json == null) {
    return json;
  }
  return {
    id: json['id'],
    message:
      json['message'] == null ? undefined : MessagesFromJSON(json['message']),
    message_id: json['message_id'],
    type: MessageContentTypeFromJSON(json['type']),
    tool_use_id: json['tool_use_id'] == null ? undefined : json['tool_use_id'],
    tool_use_is_error:
      json['tool_use_is_error'] == null ? undefined : json['tool_use_is_error'],
    tool_use_name:
      json['tool_use_name'] == null ? undefined : json['tool_use_name'],
    tool_use_input:
      json['tool_use_input'] == null ? undefined : json['tool_use_input'],
    content: json['content'] == null ? undefined : json['content'],
    content_type:
      json['content_type'] == null ? undefined : json['content_type'],
    content_format: MessageContentFormatFromJSON(json['content_format']),
    data: json['data'] == null ? undefined : json['data'],
    created_at: new Date(json['created_at']),
    updated_at: new Date(json['updated_at'])
  };
}

export function MessageContentsToJSON(json: any): MessageContents {
  return MessageContentsToJSONTyped(json, false);
}

export function MessageContentsToJSONTyped(
  value?: MessageContents | null,
  ignoreDiscriminator: boolean = false
): any {
  if (value == null) {
    return value;
  }

  return {
    id: value['id'],
    message: MessagesToJSON(value['message']),
    message_id: value['message_id'],
    type: MessageContentTypeToJSON(value['type']),
    tool_use_id: value['tool_use_id'],
    tool_use_is_error: value['tool_use_is_error'],
    tool_use_name: value['tool_use_name'],
    tool_use_input: JSON.stringify(value['tool_use_input']),
    content: value['content'],
    content_type: value['content_type'],
    content_format: MessageContentFormatToJSON(value['content_format']),
    data: value['data'],
    created_at: value['created_at'].toISOString(),
    updated_at: value['updated_at'].toISOString()
  };
}
