/* tslint:disable */
/* eslint-disable */
/**
 * FastAPI
 * No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)
 *
 * The version of the OpenAPI document: 0.1.0
 * 
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */

import { mapValues } from '../runtime';
/**
 * 
 * @export
 * @interface MessageContent
 */
export interface MessageContent {
    /**
     * The type of content in the message.
     * @type {string}
     * @memberof MessageContent
     */
    type?: MessageContentTypeEnum;
    /**
     * The content of the message.
     * @type {string}
     * @memberof MessageContent
     */
    content: string;
}


/**
 * @export
 */
export const MessageContentTypeEnum = {
    Text: 'text'
} as const;
export type MessageContentTypeEnum = typeof MessageContentTypeEnum[keyof typeof MessageContentTypeEnum];


/**
 * Check if a given object implements the MessageContent interface.
 */
export function instanceOfMessageContent(value: object): value is MessageContent {
    if (!('content' in value) || value['content'] === undefined) return false;
    return true;
}

export function MessageContentFromJSON(json: any): MessageContent {
    return MessageContentFromJSONTyped(json, false);
}

export function MessageContentFromJSONTyped(json: any, ignoreDiscriminator: boolean): MessageContent {
    if (json == null) {
        return json;
    }
    return {
        
        'type': json['type'] == null ? undefined : json['type'],
        'content': json['content'],
    };
}

export function MessageContentToJSON(json: any): MessageContent {
    return MessageContentToJSONTyped(json, false);
}

export function MessageContentToJSONTyped(value?: MessageContent | null, ignoreDiscriminator: boolean = false): any {
    if (value == null) {
        return value;
    }

    return {
        
        'type': value['type'],
        'content': value['content'],
    };
}

