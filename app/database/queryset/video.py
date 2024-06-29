
from django.db import transaction

from app.database.models import (
    Video,
    Actor,
    Staff,
    Genre,
    Production,
    VideoGenre,
)


# Video
def create_video(new_video):
    try:
        video = Video.objects.create(
            code=new_video['code'],
            title=new_video['title'],
            synopsis=new_video['synopsis'],
            release=new_video['release'],
            runtime=new_video['runtime'],
            notice_age=new_video['notice_age'],
        )
        video.save()
        return video
    except Exception as e:
        raise e


def read_video(video_id):
    try:
        video = Video.objects.get(id=video_id)
        return video
    except Exception as e:
        raise e


def update_video(video, new_video):
    try:
        is_updated = False
        if not video:
            return False
        if new_video.get('code'):
            if video.code != new_video['code']:
                video.code = new_video['code']
                is_updated = True
        if new_video.get('title'):
            if video.title != new_video['title']:
                video.title = new_video['title']
                is_updated = True
        if new_video.get('synopsis'):
            if video.synopsis != new_video['synopsis']:
                video.synopsis = new_video['synopsis']
                is_updated = True
        if new_video.get('release'):
            if video.release != new_video['release']:
                video.release = new_video['release']
                is_updated = True
        if new_video.get('runtime'):
            if video.runtime != new_video['runtime']:
                video.runtime = new_video['runtime']
                is_updated = True
        if new_video.get('notice_age'):
            if video.notice_age != new_video['notice_age']:
                video.notice_age = new_video['notice_age']
                is_updated = True
        if new_video.get('country'):
            if video.country != new_video['country']:
                video.country = new_video['country']
                is_updated = True
        if new_video.get('is_confirm', None) is not None:
            if video.is_confirm != new_video['is_confirm']:
                video.is_confirm = new_video['is_confirm']
                is_updated = True
        if is_updated:
            video.save()
        return True
    except Exception as e:
        raise e


def delete_video(video):
    try:
        video.objects.delete()
        return True
    except Exception as e:
        raise e


# Actor
def create_actor(new_actor):
    try:
        actor = Actor.objects.create(
            name=new_actor['name'],
            picture=new_actor['picture'],
            profile=new_actor['profile'],
        )
        actor.save()
        return actor
    except Exception as e:
        raise e


def read_actor(actor_id):
    try:
        return Actor.objects.get(id=actor_id)
    except Exception as e:
        raise e


def update_actor(actor, new_actor):
    try:
        is_updated = False
        if not actor:
            return False
        if new_actor.get('name'):
            if actor.name != new_actor['name']:
                actor.name = new_actor['name']
                is_updated = True
        if new_actor.get('picture'):
            if actor.picture != new_actor['picture']:
                actor.picture = new_actor['picture']
                is_updated = True
        if new_actor.get('profile'):
            if actor.profile != new_actor['profile']:
                actor.profile = new_actor['profile']
                is_updated = True
        if is_updated:
            actor.save()
        return True
    except Exception as e:
        raise e


def delete_actor(actor):
    try:
        actor.objects.delete()
        return True
    except Exception as e:
        raise e


# Staff
def create_staff(new_staff):
    try:
        staff = Staff.objects.create(
            name=new_staff['name'],
            picture=new_staff['picture'],
            profile=new_staff['profile'],
        )
        staff.save()
        return staff
    except Exception as e:
        raise e


def read_staff(staff_id):
    try:
        return Staff.objects.get(id=staff_id)
    except Exception as e:
        raise e


def update_staff(staff, new_staff):
    try:
        is_updated = False
        if not staff:
            return False
        if new_staff.get('name'):
            if staff.name != new_staff['name']:
                staff.name = new_staff['name']
                is_updated = True
        if new_staff.get('picture'):
            if staff.picture != new_staff['picture']:
                staff.picture = new_staff['picture']
                is_updated = True
        if new_staff.get('profile'):
            if staff.profile != new_staff['profile']:
                staff.profile = new_staff['profile']
                is_updated = True
        if is_updated:
            staff.save()
        return True
    except Exception as e:
        raise e


def delete_staff(staff):
    try:
        staff.objects.delete()
        return True
    except Exception as e:
        raise e


# Genre
def create_genre(new_genre):
    try:
        genre = Genre.objects.create(
            name=new_genre['name'],
        ).save()
        return genre
    except Exception as e:
        raise e


def read_genre(genre_id):
    try:
        return Genre.objects.get(id=genre_id)
    except Exception as e:
        raise e


def update_genre(genre, new_genre):
    try:
        is_updated = False
        if not genre:
            return False
        if new_genre.get('name'):
            genre.name = new_genre['name']
            is_updated = True
        if is_updated:
            genre.save()
        return True
    except Exception as e:
        raise e


def delete_genre(genre):
    try:
        genre.objects.delete()
        return True
    except Exception as e:
        raise e


# Production
def create_production(new_production):
    try:
        production = Production.objects.create(
            name=new_production['name'],
            logo=new_production['logo'],
        )
        production.save()
        return production
    except Exception as e:
        raise e


def read_production(production_id):
    try:
        return Production.objects.get(id=production_id)
    except Exception as e:
        raise e


def update_production(production, new_production):
    try:
        is_updated = False
        if not production:
            return False
        if new_production.get('name'):
            if production.name != new_production['name']:
                production.name = new_production['name']
                is_updated = True
        if new_production.get('logo'):
            if production.logo != new_production['logo']:
                production.logo = new_production['logo']
                is_updated = True
        if is_updated:
            production.save()
        return True
    except Exception as e:
        raise e


def delete_production(production):
    try:
        production.objects.delete()
        return True
    except Exception as e:
        raise e


# VideoActor
def create_video_actor(video, new_actor):
    try:
        if new_actor.get('actor_id', False):
            actor = Actor.objects.get(id=new_actor['actor_id'])
        else:
            actor, created = Actor.objects.get_or_create(name=new_actor['name'])
        video.actor_list.create(
            actor=actor,
            code=new_actor['code'],
            role=new_actor['role'],
            sort=new_actor['sort'] if new_actor.get('sort') else 99
        ).save()
        return True
    except Exception as e:
        print(e)
        raise e


def update_video_actor(vide_actor, new_actor):
    try:
        is_updated = False
        if new_actor.get('code'):
            if vide_actor.code != new_actor['code']:
                vide_actor.code = new_actor['code']
                is_updated = True
        if new_actor.get('role'):
            if vide_actor.role != new_actor['role']:
                vide_actor.role = new_actor['role']
                is_updated = True
        if new_actor.get('sort'):
            if vide_actor.sort != new_actor['sort']:
                vide_actor.sort = new_actor['sort'] if new_actor.get('sort') else 99
                is_updated = True
        if is_updated:
            vide_actor.save()
        return True
    except Exception as e:
        raise e


def delete_video_actor(video, video_actor_id):
    try:
        video.actor_list.get(id=video_actor_id).delete()
        return True
    except Exception as e:
        raise e


# VideoStaff
def create_video_staff(video, new_staff):
    try:
        if new_staff.get('staff_id', False):
            staff = Staff.objects.get(id=new_staff['staff_id'])
        else:
            staff, created = Staff.objects.get_or_create(name=new_staff['name'])
        video.staff_list.create(
            staff=staff,
            code=new_staff['code'],
            sort=new_staff['sort'] if new_staff.get('sort') else 99
        ).save()
        return True
    except Exception as e:
        raise e


def update_video_staff(video_staff, new_staff):
    try:
        is_updated = False
        if new_staff.get('code'):
            if video_staff.code != new_staff['code']:
                video_staff.code = new_staff['code']
                is_updated = True
        if new_staff.get('sort'):
            if video_staff.sort != new_staff['sort']:
                video_staff.sort = new_staff['sort'] if new_staff.get('sort') else 99
                is_updated = True
        if is_updated:
            video_staff.save()
        return True
    except Exception as e:
        raise e


def delete_video_staff(video, video_staff_id):
    try:
        video.staff_list.get(id=video_staff_id).delete()
        return True
    except Exception as e:
        raise e


# VideoGenre
def create_video_genre(video, new_genre):
    try:
        genre, created = Genre.objects.get_or_create(name=new_genre['name'])
        VideoGenre.objects.create(
            video=video,
            genre=genre,
            sort=new_genre['sort'] if new_genre.get('sort') else 99
        )
        return True
    except Exception as e:
        raise e


def update_video_genre(video_genre, new_genre):
    try:
        is_updated = False
        if new_genre.get('sort'):
            if video_genre.sort != new_genre['sort']:
                video_genre.sort = new_genre['sort']
                is_updated = True
        if is_updated:
            video_genre.save()
        return True
    except Exception as e:
        raise e

    
def delete_video_genre(video, video_genre_id):
    try:
        video.genre_list.get(id=video_genre_id).delete()
        return True
    except Exception as e:
        raise e


# VideoPlatform
def create_video_platform(video, new_platform):
    try:
        video.platform.create(
            code=new_platform['code'],
            ext_id=new_platform['ext_id'],
            url=new_platform['url'],
        ).save()
        return True
    except Exception as e:
        raise e


def update_video_platform(video_platform, new_platform):
    try:
        is_updated = False
        if not video_platform:
            return False
        if new_platform.get('code'):
            if video_platform.code != new_platform['code']:
                video_platform.code = new_platform['code']
                is_updated = True
        if new_platform.get('url'):
            if video_platform.url != new_platform['url']:
                video_platform.url = new_platform['url']
                is_updated = True
        if new_platform.get('ext_id'):
            if video_platform.ext_id != new_platform['ext_id']:
                video_platform.ext_id = new_platform['ext_id']
                is_updated = True
        if is_updated:
            video_platform.save()
        return True
    except Exception as e:
        raise e


def delete_video_platform(video, platform_id):
    try:
        video.platform.get(id=platform_id).delete()
        return True
    except Exception as e:
        raise e


# VideoProduction
def create_video_production(video, new_production):
    try:
        production, created = Production.objects.get_or_create(name=new_production['name'])
        video.production_list.create(
            production=production
        ).save()
        return True
    except Exception as e:
        raise e


def delete_video_production(video, video_production_id):
    try:
        video.production_list.get(id=video_production_id).delete()
        return True
    except Exception as e:
        raise e


# VideoThumbnail
def create_video_thumbnail(video, new_thumbnail):
    try:
        return video.thumbnail.create(
            code=new_thumbnail['code'],
            url=new_thumbnail['url'],
            extension=new_thumbnail['extension'],
            size=new_thumbnail['size'],
            width=new_thumbnail['width'],
            height=new_thumbnail['height'],
            sort=new_thumbnail['sort'] if new_thumbnail.get('sort') else 99
        )
    except Exception as e:
        raise e


def update_video_thumbnail(video_thumbnail, new_thumbnail):
    try:
        is_updated = False
        if not new_thumbnail.get('code'):
            if video_thumbnail.code != new_thumbnail['code']:
                video_thumbnail.code = new_thumbnail['code']
                is_updated = True
        if new_thumbnail.get('url'):
            if video_thumbnail.url != new_thumbnail['url']:
                video_thumbnail.url = new_thumbnail['url']
                is_updated = True
        if new_thumbnail.get('extension'):
            if video_thumbnail.extension != new_thumbnail['extension']:
                video_thumbnail.extension = new_thumbnail['extension']
                is_updated = True
        if new_thumbnail.get('size'):
            if video_thumbnail.size != new_thumbnail['size']:
                video_thumbnail.size = new_thumbnail['size']
                is_updated = True
        if new_thumbnail.get('width'):
            if video_thumbnail.width != new_thumbnail['width']:
                video_thumbnail.width = new_thumbnail['width']
                is_updated = True
        if new_thumbnail.get('height'):
            if video_thumbnail.height != new_thumbnail['height']:
                video_thumbnail.height = new_thumbnail['height']
                is_updated = True
        if new_thumbnail.get('sort'):
            if video_thumbnail.sort != new_thumbnail['sort']:
                video_thumbnail.sort = new_thumbnail['sort']
                is_updated = True
        if is_updated:
            video_thumbnail.save()
        return True
    except Exception as e:
        raise e


def delete_video_thumbnail(video, video_thumbnail_id):
    try:
        video.thumbnail.get(id=video_thumbnail_id).delete()
        return True
    except Exception as e:
        raise e


def create_video_object_all(new_object):
    try:
        with transaction.atomic():
            video = create_video(new_object)
            for new_actor in new_object.get('actor'):
                create_video_actor(video, new_actor)
            for new_staff in new_object.get('staff'):
                create_video_staff(video, new_staff)
            for new_genre in new_object.get('genre'):
                create_video_genre(video, new_genre)
            for new_platform in new_object.get('platform', []):
                create_video_platform(video, new_platform)
            for new_production in new_object.get('production', []):
                create_video_production(video, new_production)
            for new_thumbnail in new_object.get('thumbnail', []):
                create_video_thumbnail(video, new_thumbnail)
            return video
    except Exception as e:
        print(e)
        raise e


# search
def search_video_by_platform(code, ext_id):
    videos = search_videos_by_platform(code, ext_id)
    if not videos:
        return None
    return videos.first()


def search_videos_by_platform(code, ext_id):
    try:
        videos = Video.objects.filter(platform__code=code, platform__ext_id=ext_id)
        if not videos:
            return None
        return videos.all()
    except Exception as e:
        print(e)
        raise e


def search_video_by_title(title):
    return search_videos_by_title(title).first()


def search_videos_by_title(title):
    return Video.objects.filter(title=title)


# exist
def exist_video_genre(video, genre_name):
    try:
        for genre in video.genre_list.all():
            if genre.name == genre_name:
                return True
        return False
    except Exception as e:
        raise e
