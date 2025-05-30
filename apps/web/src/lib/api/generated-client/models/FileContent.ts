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
/**
 * @export
 * @interface FileContent
 */
export interface FileContent {
  /**
   * The ID of the content.
   *
   * @memberof FileContent
   * @type {string}
   */
  id: string;
  /**
   * @memberof FileContent
   * @type {string}
   */
  type?: FileContentTypeEnum;
  /**
   * The file data of the message.
   *
   * @memberof FileContent
   * @type {string}
   */
  file_data: string;
  /**
   * The name of the file.
   *
   * @memberof FileContent
   * @type {string}
   */
  file_name: string;
}

/** @export */
export const FileContentTypeEnum = {
  File: 'file'
} as const;
export type FileContentTypeEnum =
  (typeof FileContentTypeEnum)[keyof typeof FileContentTypeEnum];

/** Check if a given object implements the FileContent interface. */
export function instanceOfFileContent(value: object): value is FileContent {
  if (!('id' in value) || value['id'] === undefined) return false;
  if (!('file_data' in value) || value['file_data'] === undefined) return false;
  if (!('file_name' in value) || value['file_name'] === undefined) return false;
  return true;
}

export function FileContentFromJSON(json: any): FileContent {
  return FileContentFromJSONTyped(json, false);
}

export function FileContentFromJSONTyped(
  json: any,
  ignoreDiscriminator: boolean
): FileContent {
  if (json == null) {
    return json;
  }
  return {
    id: json['id'],
    type: json['type'] == null ? undefined : json['type'],
    file_data: json['file_data'],
    file_name: json['file_name']
  };
}

export function FileContentToJSON(json: any): FileContent {
  return FileContentToJSONTyped(json, false);
}

export function FileContentToJSONTyped(
  value?: FileContent | null,
  ignoreDiscriminator: boolean = false
): any {
  if (value == null) {
    return value;
  }

  return {
    id: value['id'],
    type: value['type'],
    file_data: value['file_data'],
    file_name: value['file_name']
  };
}
