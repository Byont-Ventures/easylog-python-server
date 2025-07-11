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
/**
 * @export
 * @interface MediaResourceOpenLabel
 */
export interface MediaResourceOpenLabel {
  /**
   * @memberof MediaResourceOpenLabel
   * @type {string}
   */
  en?: string;
  /**
   * @memberof MediaResourceOpenLabel
   * @type {string}
   */
  nl?: string;
}

/** Check if a given object implements the MediaResourceOpenLabel interface. */
export function instanceOfMediaResourceOpenLabel(
  value: object
): value is MediaResourceOpenLabel {
  return true;
}

export function MediaResourceOpenLabelFromJSON(
  json: any
): MediaResourceOpenLabel {
  return MediaResourceOpenLabelFromJSONTyped(json, false);
}

export function MediaResourceOpenLabelFromJSONTyped(
  json: any,
  ignoreDiscriminator: boolean
): MediaResourceOpenLabel {
  if (json == null) {
    return json;
  }
  return {
    en: json['en'] == null ? undefined : json['en'],
    nl: json['nl'] == null ? undefined : json['nl']
  };
}

export function MediaResourceOpenLabelToJSON(
  json: any
): MediaResourceOpenLabel {
  return MediaResourceOpenLabelToJSONTyped(json, false);
}

export function MediaResourceOpenLabelToJSONTyped(
  value?: MediaResourceOpenLabel | null,
  ignoreDiscriminator: boolean = false
): any {
  if (value == null) {
    return value;
  }

  return {
    en: value['en'],
    nl: value['nl']
  };
}
