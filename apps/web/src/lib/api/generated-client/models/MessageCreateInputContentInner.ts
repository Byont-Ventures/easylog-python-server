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

import type { MessageCreateInputFileContent } from './MessageCreateInputFileContent';
import {
  instanceOfMessageCreateInputFileContent,
  MessageCreateInputFileContentFromJSON,
  MessageCreateInputFileContentFromJSONTyped,
  MessageCreateInputFileContentToJSON
} from './MessageCreateInputFileContent';
import type { MessageCreateInputImageContent } from './MessageCreateInputImageContent';
import {
  instanceOfMessageCreateInputImageContent,
  MessageCreateInputImageContentFromJSON,
  MessageCreateInputImageContentFromJSONTyped,
  MessageCreateInputImageContentToJSON
} from './MessageCreateInputImageContent';
import type { MessageCreateInputTextContent } from './MessageCreateInputTextContent';
import {
  instanceOfMessageCreateInputTextContent,
  MessageCreateInputTextContentFromJSON,
  MessageCreateInputTextContentFromJSONTyped,
  MessageCreateInputTextContentToJSON
} from './MessageCreateInputTextContent';

/**
 * @type MessageCreateInputContentInner
 * @export
 */
export type MessageCreateInputContentInner =
  | ({ type: 'file' } & MessageCreateInputFileContent)
  | ({ type: 'image' } & MessageCreateInputImageContent)
  | ({ type: 'text' } & MessageCreateInputTextContent);

export function MessageCreateInputContentInnerFromJSON(
  json: any
): MessageCreateInputContentInner {
  return MessageCreateInputContentInnerFromJSONTyped(json, false);
}

export function MessageCreateInputContentInnerFromJSONTyped(
  json: any,
  ignoreDiscriminator: boolean
): MessageCreateInputContentInner {
  if (json == null) {
    return json;
  }
  switch (json['type']) {
    case 'file':
      return Object.assign(
        {},
        MessageCreateInputFileContentFromJSONTyped(json, true),
        { type: 'file' } as const
      );
    case 'image':
      return Object.assign(
        {},
        MessageCreateInputImageContentFromJSONTyped(json, true),
        { type: 'image' } as const
      );
    case 'text':
      return Object.assign(
        {},
        MessageCreateInputTextContentFromJSONTyped(json, true),
        { type: 'text' } as const
      );
    default:
      throw new Error(
        `No variant of MessageCreateInputContentInner exists with 'type=${json['type']}'`
      );
  }
}

export function MessageCreateInputContentInnerToJSON(json: any): any {
  return MessageCreateInputContentInnerToJSONTyped(json, false);
}

export function MessageCreateInputContentInnerToJSONTyped(
  value?: MessageCreateInputContentInner | null,
  ignoreDiscriminator: boolean = false
): any {
  if (value == null) {
    return value;
  }
  switch (value['type']) {
    case 'file':
      return Object.assign({}, MessageCreateInputFileContentToJSON(value), {
        type: 'file'
      } as const);
    case 'image':
      return Object.assign({}, MessageCreateInputImageContentToJSON(value), {
        type: 'image'
      } as const);
    case 'text':
      return Object.assign({}, MessageCreateInputTextContentToJSON(value), {
        type: 'text'
      } as const);
    default:
      throw new Error(
        `No variant of MessageCreateInputContentInner exists with 'type=${value['type']}'`
      );
  }
}
