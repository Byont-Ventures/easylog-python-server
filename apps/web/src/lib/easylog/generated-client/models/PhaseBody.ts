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
 * @interface PhaseBody
 */
export interface PhaseBody {
  /**
   * @memberof PhaseBody
   * @type {string}
   */
  slug: string;
  /**
   * @memberof PhaseBody
   * @type {Date}
   */
  start: Date;
  /**
   * @memberof PhaseBody
   * @type {Date}
   */
  end: Date;
  /**
   * @memberof PhaseBody
   * @type {boolean}
   */
  isStaged?: boolean;
}

/** Check if a given object implements the PhaseBody interface. */
export function instanceOfPhaseBody(value: object): value is PhaseBody {
  if (!('slug' in value) || value['slug'] === undefined) return false;
  if (!('start' in value) || value['start'] === undefined) return false;
  if (!('end' in value) || value['end'] === undefined) return false;
  return true;
}

export function PhaseBodyFromJSON(json: any): PhaseBody {
  return PhaseBodyFromJSONTyped(json, false);
}

export function PhaseBodyFromJSONTyped(
  json: any,
  ignoreDiscriminator: boolean
): PhaseBody {
  if (json == null) {
    return json;
  }
  return {
    slug: json['slug'],
    start: new Date(json['start']),
    end: new Date(json['end']),
    isStaged: json['is_staged'] == null ? undefined : json['is_staged']
  };
}

export function PhaseBodyToJSON(json: any): PhaseBody {
  return PhaseBodyToJSONTyped(json, false);
}

export function PhaseBodyToJSONTyped(
  value?: PhaseBody | null,
  ignoreDiscriminator: boolean = false
): any {
  if (value == null) {
    return value;
  }

  return {
    slug: value['slug'],
    start: value['start'].toISOString(),
    end: value['end'].toISOString(),
    is_staged: value['isStaged']
  };
}
